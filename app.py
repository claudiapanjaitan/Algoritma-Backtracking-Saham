import csv
from flask import Flask, render_template, request
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

# Fungsi untuk memuat data dari file CSV
def load_stock_data(file_name):
    stocks = []
    with open(file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if all(row[key] for key in row):  # Pastikan semua nilai kolom tidak kosong
                stock = {
                    'Code': row['Code'],
                    'Name': row['Name'],
                    'ListingDate': row['ListingDate'],
                    'Shares': float(row['Shares']),
                    'ListingBoard': row['ListingBoard'],
                    'Sector': row['Sector'],
                    'LastPrice': float(row['LastPrice']),
                    'MarketCap': row['MarketCap'],
                    'MinutesFirstAdded': row['MinutesFirstAdded'],
                    'MinutesLastUpdated': row['MinutesLastUpdated'],
                    'HourlyFirstAdded': row['HourlyFirstAdded'],
                    'HourlyLastUpdated': row['HourlyLastUpdated'],
                    'DailyFirstAdded': row['DailyFirstAdded'],
                    'DailyLastUpdated': row['DailyLastUpdated']
                }
                stocks.append(stock)
    return stocks

# Fungsi backtracking untuk mencari kombinasi saham dengan total harga tertinggi tanpa melebihi batasan jumlah
def backtrack(stock_data, current_index, current_portfolio, max_price, current_price, best_portfolio):
    if current_price > max_price:
        return

    if current_index == len(stock_data):
        if sum(stock['LastPrice'] * stock['Shares'] for stock in current_portfolio) > sum(stock['LastPrice'] * stock['Shares'] for stock in best_portfolio):
            best_portfolio[:] = current_portfolio[:]
        return

    current_stock = stock_data[current_index]

    # Tambah saham ke portofolio
    current_portfolio.append(current_stock)

    # Cari kombinasi dengan menambah saham selanjutnya
    backtrack(stock_data, current_index + 1, current_portfolio, max_price, current_price + current_stock['LastPrice'] * current_stock['Shares'], best_portfolio)

    # Hapus saham terakhir untuk mencoba kombinasi lain
    current_portfolio.pop()

    # Cari kombinasi tanpa menambah saham ini
    backtrack(stock_data, current_index + 1, current_portfolio, max_price, current_price, best_portfolio)

# Fungsi untuk menampilkan grafik dari kombinasi saham terbaik
def plot_stock_portfolio(portfolio):
    labels = [stock['Code'] + ' - ' + stock['Name'] for stock in portfolio]
    sizes = [stock['LastPrice'] * stock['Shares'] for stock in portfolio]

    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Membuat pie chart menjadi lingkaran

    # Simpan grafik sebagai file gambar
    img = BytesIO()
    plt.savefig(img, format='png')
    plt.close()  # Tutup gambar Matplotlib
    img.seek(0)
    return img.getvalue()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        max_allowed_price = float(request.form['max_price'])

        file_name = 'DaftarSaham.csv'  # Ganti dengan nama file yang sesuai
        stock_data = load_stock_data(file_name)

        best_portfolio = []
        backtrack(stock_data, 0, [], max_allowed_price, 0, best_portfolio)

        img_data = plot_stock_portfolio(best_portfolio)

        # Hasil kombinasi saham terbaik
        result = "Kombinasi Saham Terbaik:<br><br><br>"
        for stock in best_portfolio:
            result += f"{stock['Code']} - {stock['Name']}<br>"

        # Konversi data gambar ke base64 untuk ditampilkan di HTML
        img_data_base64 = base64.b64encode(img_data).decode('utf-8')

        # Tampilkan hasil dan gambar
        return render_template('index.html', result=result, img_data=img_data_base64)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
