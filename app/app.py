from flask import Flask, request, redirect, jsonify, render_template, send_file
import pandas as pd
import os

app = Flask(__name__)

# Diretório para armazenar a base de dados processada
data_folder = "./data"  # corrigido para usar diretório local
os.makedirs(data_folder, exist_ok=True)
db_file = os.path.join(data_folder, "money_cleaned.csv")

# Função para carregar e processar a base de dados
def load_and_clean_data():
    if os.path.exists(db_file):
        return pd.read_csv(db_file)
    return pd.DataFrame(columns=["user_id", "wallet", "bank", "paypal"])

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# Tela inicial (upload + animação)
@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/loading', methods=['POST'])
def loading_screen():
    file = request.files.get('file')
    if not file:
        return redirect('/')
    
    # Salva e processa o arquivo
    temp_file = os.path.join(data_folder, "money_temp.csv")
    file.save(temp_file)

    df = pd.read_csv(temp_file)
    df = df.drop(columns=["t1", "t2", "t3", "t4", "coins", "fines", "diamonds"], errors='ignore')
    df = df[df["bank"] != 10000]
    df.to_csv(db_file, index=False)

    return render_template('loading.html')


# Rota para upload da base de dados e curadoria dos dados
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nome do arquivo inválido."}), 400

    # Salvar arquivo temporário
    temp_file = os.path.join(data_folder, "money_temp.csv")
    file.save(temp_file)

    # Processar e limpar os dados
    df = pd.read_csv(temp_file)
    df = df.drop(columns=["t1", "t2", "t3", "t4", "coins", "fines", "diamonds"], errors='ignore')
    df = df[df["bank"] != 10000]  # Remover jogadores com exatos 10.000 no banco

    # Salvar arquivo processado
    df.to_csv(db_file, index=False)

    return jsonify({"message": "Base de dados processada e atualizada com sucesso."})

# Rota para baixar o CSV curado
@app.route('/download', methods=['GET'])
def download_cleaned_csv():
    if os.path.exists(db_file):
        return send_file(db_file, as_attachment=True)
    return jsonify({"error": "Arquivo não encontrado."}), 404

# Rota para calcular métricas e retornar JSON
@app.route('/metrics', methods=['GET'])
def get_metrics():
    df = load_and_clean_data()
    if df.empty:
        return jsonify({"error": "Nenhum dado disponível."}), 400

    df["total_money"] = df["wallet"] + df["bank"] + df["paypal"]
    total_players = int(df.shape[0])
    bankrupt_players = int((df["total_money"] < 100_000).sum())

    poverty = int((df["total_money"] < 500_000).sum())
    lower_middle = int(((df["total_money"] >= 500_000) & (df["total_money"] < 1_000_000)).sum())
    upper_middle = int(((df["total_money"] >= 1_000_000) & (df["total_money"] < 10_000_000)).sum())
    rich = int(((df["total_money"] >= 10_000_000) & (df["total_money"] < 100_000_000)).sum())
    magnates = int((df["total_money"] >= 100_000_000).sum())

    df_sorted = df.sort_values(by="total_money")
    cum_total = df_sorted["total_money"].cumsum()
    gini_index = 1 - 2 * (cum_total / cum_total.iloc[-1]).mean()

    top_20 = df.nlargest(20, "total_money")["total_money"].sum()
    total_money_sum = df["total_money"].sum()
    top_1_percent_vs_rest = (top_20 / total_money_sum) * 100 if total_money_sum > 0 else 0

    wallet_percent = (df["wallet"].sum() / total_money_sum) * 100
    bank_percent = (df["bank"].sum() / total_money_sum) * 100
    paypal_percent = (df["paypal"].sum() / total_money_sum) * 100

    metrics = {
        "total_money": int(total_money_sum),
        "average_wealth": float(df["total_money"].mean()),
        "median_wealth": float(df["total_money"].median()),
        "top_10_richest": df.nlargest(10, "total_money")[["user_id", "total_money"]].to_dict(orient='records'),
        "total_players": total_players,
        "bankrupt_players": bankrupt_players,
        "poverty": poverty,
        "lower_middle": lower_middle,
        "upper_middle": upper_middle,
        "rich": rich,
        "magnates": magnates,
        "gini_index": gini_index,
        "top_1_percent_vs_rest": top_1_percent_vs_rest,
        "wallet_percent": wallet_percent,
        "bank_percent": bank_percent,
        "paypal_percent": paypal_percent,
    }

    return jsonify(metrics)

# 🔥 Ponto único de entrada da aplicação
if __name__ == '__main__':
    app.run(debug=True)
