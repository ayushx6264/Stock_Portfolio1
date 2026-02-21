"""
Stock Portfolio Engine — manages holdings, calculates P&L, and provides portfolio data.
"""

import random


# ── Simulated market data ──────────────────────────────────────
STOCKS = {
    "AAPL":  {"name": "Apple Inc.",          "sector": "Technology",      "price": 191.56, "change": +1.23},
    "MSFT":  {"name": "Microsoft Corp.",     "sector": "Technology",      "price": 422.86, "change": +0.87},
    "GOOGL": {"name": "Alphabet Inc.",       "sector": "Technology",      "price": 176.42, "change": -0.34},
    "AMZN":  {"name": "Amazon.com Inc.",     "sector": "Consumer Cycl.",  "price": 186.53, "change": +2.15},
    "TSLA":  {"name": "Tesla Inc.",          "sector": "Automotive",      "price": 177.90, "change": -1.62},
    "NVDA":  {"name": "NVIDIA Corp.",        "sector": "Technology",      "price": 878.37, "change": +3.41},
    "META":  {"name": "Meta Platforms",      "sector": "Technology",      "price": 502.30, "change": +1.08},
    "JPM":   {"name": "JPMorgan Chase",      "sector": "Financial",       "price": 198.47, "change": +0.55},
    "V":     {"name": "Visa Inc.",           "sector": "Financial",       "price": 281.95, "change": +0.32},
    "JNJ":   {"name": "Johnson & Johnson",  "sector": "Healthcare",      "price": 156.74, "change": -0.18},
    "WMT":   {"name": "Walmart Inc.",        "sector": "Consumer Def.",   "price": 172.63, "change": +0.91},
    "PG":    {"name": "Procter & Gamble",    "sector": "Consumer Def.",   "price": 162.38, "change": +0.14},
    "DIS":   {"name": "Walt Disney Co.",     "sector": "Entertainment",   "price": 112.22, "change": -0.76},
    "NFLX":  {"name": "Netflix Inc.",        "sector": "Entertainment",   "price": 628.15, "change": +2.67},
    "AMD":   {"name": "Advanced Micro Dev.", "sector": "Technology",      "price": 177.58, "change": +1.94},
}


class Portfolio:
    """In-memory stock portfolio manager."""

    def __init__(self):
        # holdings: { symbol: { "quantity": int, "avg_cost": float } }
        self.holdings: dict[str, dict] = {}

    # ── Actions ────────────────────────────────────────────────

    def buy(self, symbol: str, quantity: int) -> dict:
        """Buy shares of a stock. Returns a result dict."""
        symbol = symbol.upper()
        if symbol not in STOCKS:
            return {"success": False, "error": f"Unknown stock symbol: {symbol}"}
        if quantity <= 0:
            return {"success": False, "error": "Quantity must be positive."}

        price = STOCKS[symbol]["price"]
        cost = price * quantity

        if symbol in self.holdings:
            h = self.holdings[symbol]
            total_cost = h["avg_cost"] * h["quantity"] + cost
            h["quantity"] += quantity
            h["avg_cost"] = total_cost / h["quantity"]
        else:
            self.holdings[symbol] = {"quantity": quantity, "avg_cost": price}

        return {
            "success": True,
            "message": f"Bought {quantity} shares of {symbol} at ${price:.2f}",
            "cost": round(cost, 2),
        }

    def sell(self, symbol: str, quantity: int) -> dict:
        """Sell shares of a stock. Returns a result dict."""
        symbol = symbol.upper()
        if symbol not in self.holdings:
            return {"success": False, "error": f"You don't own any {symbol} shares."}
        if quantity <= 0:
            return {"success": False, "error": "Quantity must be positive."}

        h = self.holdings[symbol]
        if quantity > h["quantity"]:
            return {"success": False, "error": f"You only own {h['quantity']} shares of {symbol}."}

        price = STOCKS[symbol]["price"]
        revenue = price * quantity
        profit = (price - h["avg_cost"]) * quantity

        h["quantity"] -= quantity
        if h["quantity"] == 0:
            del self.holdings[symbol]

        return {
            "success": True,
            "message": f"Sold {quantity} shares of {symbol} at ${price:.2f}",
            "revenue": round(revenue, 2),
            "profit": round(profit, 2),
        }

    # ── Queries ────────────────────────────────────────────────

    def get_holdings(self) -> list[dict]:
        """Return a list of current holdings with computed fields."""
        results = []
        for symbol, h in self.holdings.items():
            stock = STOCKS[symbol]
            current_price = stock["price"]
            market_value = current_price * h["quantity"]
            cost_basis = h["avg_cost"] * h["quantity"]
            profit_loss = market_value - cost_basis
            profit_pct = (profit_loss / cost_basis * 100) if cost_basis else 0

            results.append({
                "symbol": symbol,
                "name": stock["name"],
                "sector": stock["sector"],
                "quantity": h["quantity"],
                "avg_cost": round(h["avg_cost"], 2),
                "current_price": round(current_price, 2),
                "change_pct": stock["change"],
                "market_value": round(market_value, 2),
                "cost_basis": round(cost_basis, 2),
                "profit_loss": round(profit_loss, 2),
                "profit_pct": round(profit_pct, 2),
            })

        # Sort by market value descending
        results.sort(key=lambda x: x["market_value"], reverse=True)
        return results

    def get_summary(self) -> dict:
        """Return overall portfolio summary."""
        holdings = self.get_holdings()
        total_value = sum(h["market_value"] for h in holdings)
        total_cost = sum(h["cost_basis"] for h in holdings)
        total_pl = total_value - total_cost
        total_pl_pct = (total_pl / total_cost * 100) if total_cost else 0

        # Daily change approximation
        daily_change = sum(
            h["market_value"] * h["change_pct"] / 100 for h in holdings
        )

        # Sector allocation
        sectors: dict[str, float] = {}
        for h in holdings:
            sectors[h["sector"]] = sectors.get(h["sector"], 0) + h["market_value"]

        sector_alloc = []
        for sector, value in sorted(sectors.items(), key=lambda x: -x[1]):
            sector_alloc.append({
                "sector": sector,
                "value": round(value, 2),
                "pct": round(value / total_value * 100, 2) if total_value else 0,
            })

        return {
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "total_pl": round(total_pl, 2),
            "total_pl_pct": round(total_pl_pct, 2),
            "daily_change": round(daily_change, 2),
            "num_holdings": len(holdings),
            "sectors": sector_alloc,
        }

    @staticmethod
    def get_available_stocks() -> list[dict]:
        """Return all available stocks for purchase."""
        return [
            {
                "symbol": sym,
                "name": info["name"],
                "sector": info["sector"],
                "price": info["price"],
                "change": info["change"],
            }
            for sym, info in sorted(STOCKS.items())
        ]