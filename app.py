"""
Stock Portfolio Dashboard — Flask Web Server
Run:   python app.py
Visit: http://127.0.0.1:5050
"""

from flask import Flask, render_template, request, jsonify
from stock import Portfolio

app = Flask(__name__)
portfolio = Portfolio()


@app.route("/")
def index():
    """Serve the dashboard UI."""
    return render_template("index.html")


@app.route("/api/stocks")
def api_stocks():
    """Return all available stocks."""
    return jsonify(Portfolio.get_available_stocks())


@app.route("/api/portfolio")
def api_portfolio():
    """Return current holdings and summary."""
    return jsonify({
        "holdings": portfolio.get_holdings(),
        "summary": portfolio.get_summary(),
    })


@app.route("/api/buy", methods=["POST"])
def api_buy():
    """Buy shares of a stock."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid request."}), 400

    symbol = data.get("symbol", "")
    quantity = data.get("quantity", 0)

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid quantity."}), 400

    result = portfolio.buy(symbol, quantity)
    status = 200 if result["success"] else 400
    return jsonify(result), status


@app.route("/api/sell", methods=["POST"])
def api_sell():
    """Sell shares of a stock."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid request."}), 400

    symbol = data.get("symbol", "")
    quantity = data.get("quantity", 0)

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid quantity."}), 400

    result = portfolio.sell(symbol, quantity)
    status = 200 if result["success"] else 400
    return jsonify(result), status


if __name__ == "__main__":
    print("📈 Stock Portfolio Dashboard running at http://127.0.0.1:5050")
    app.run(debug=True, use_reloader=False, port=5050)
