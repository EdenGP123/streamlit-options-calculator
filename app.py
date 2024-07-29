import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def calculate_profit_loss(direction, option, strike, premium, quantity, contract_size, price):
    intrinsic_value = max(strike - price if option == "Put" else price - strike, 0)
    if direction == "Client Buy":
        return (intrinsic_value - premium) * quantity * contract_size
    elif direction == "Client Sell":
        return (premium - intrinsic_value) * quantity * contract_size
    return 0

def max_gain_loss_single_leg(strategy):
    direction, option, strike, premium, quantity, contract_size = strategy
    if direction == "Client Buy" and option == "Call":
        return "Long Call", "Unlimited", premium * quantity * contract_size
    elif direction == "Client Buy" and option == "Put":
        return "Long Put", (strike - premium) * quantity * contract_size, premium * quantity * contract_size
    elif direction == "Client Sell" and option == "Call":
        return "Short Call", premium * quantity * contract_size, "Unlimited"
    elif direction == "Client Sell" and option == "Put":
        return "Short Put", premium * quantity * contract_size, (strike - premium) * quantity * contract_size
    return "Varies", "Varies", "Varies"

def max_gain_loss_two_legs(sorted_legs):
    if sorted_legs[0][1] == sorted_legs[1][1] == "Call" and sorted_legs[0][0] != sorted_legs[1][0]:
        return ("Bull Call Spread",
                (sorted_legs[1][2] - sorted_legs[0][2] - sorted_legs[0][3] + sorted_legs[1][3]) * sorted_legs[0][4] * sorted_legs[0][5],
                (sorted_legs[0][3] - sorted_legs[1][3]) * sorted_legs[0][4] * sorted_legs[0][5])
    elif sorted_legs[0][1] == sorted_legs[1][1] == "Put" and sorted_legs[0][0] != sorted_legs[1][0]:
        return ("Bear Put Spread",
                (sorted_legs[0][2] - sorted_legs[1][2] - sorted_legs[0][3] + sorted_legs[1][3]) * sorted_legs[0][4] * sorted_legs[0][5],
                (sorted_legs[0][3] - sorted_legs[1][3]) * sorted_legs[0][4] * sorted_legs[0][5])
    elif sorted_legs[0][1] == "Call" and sorted_legs[1][1] == "Stock":
        return ("Covered Call",
                (sorted_legs[0][2] + sorted_legs[0][3] - sorted_legs[1][2]) * sorted_legs[0][4] * sorted_legs[0][5],
                (sorted_legs[1][2] - sorted_legs[0][3]) * sorted_legs[0][4] * sorted_legs[0][5])
    elif sorted_legs[0][1] == "Put" and sorted_legs[1][1] == "Stock":
        return ("Protective Put",
                "Unlimited",
                (sorted_legs[1][2] - sorted_legs[0][2] + sorted_legs[0][3]) * sorted_legs[0][4] * sorted_legs[0][5])
    return "Varies", "Varies", "Varies"

def max_gain_loss_three_legs(sorted_legs):
    if all(leg[1] == "Call" for leg in sorted_legs):
        return ("Long Straddle",
                "Unlimited",
                sum(leg[3] * leg[4] * leg[5] for leg in sorted_legs))
    elif all(leg[1] == "Put" for leg in sorted_legs):
        return ("Long Straddle",
                sum(leg[2] * leg[4] * leg[5] for leg in sorted_legs) - sum(leg[3] * leg[4] * leg[5] for leg in sorted_legs),
                sum(leg[3] * leg[4] * leg[5] for leg in sorted_legs))
    elif sorted_legs[0][1] == "Call" and sorted_legs[1][1] == "Put" and sorted_legs[2][1] == "Put":
        return ("Short Straddle",
                sum(leg[3] * leg[4] * leg[5] for leg in sorted_legs),
                "Unlimited")
    return "Varies", "Varies", "Varies"

def max_gain_loss_four_legs(sorted_legs):
    if sorted_legs[0][1] == sorted_legs[1][1] == "Call" and sorted_legs[2][1] == sorted_legs[3][1] == "Put":
        return ("Iron Condor",
                sum(leg[3] * leg[4] * leg[5] for leg in sorted_legs if leg[0] == "Client Sell") - sum(leg[3] * leg[4] * leg[5] for leg in sorted_legs if leg[0] == "Client Buy"),
                min((sorted_legs[1][2] - sorted_legs[0][2]) * sorted_legs[0][4] * sorted_legs[0][5],
                    (sorted_legs[3][2] - sorted_legs[2][2]) * sorted_legs[2][4] * sorted_legs[2][5]) - sum(leg[3] * leg[4] * leg[5] for leg in sorted_legs if leg[0] == "Client Sell"))
    return "Varies", "Varies", "Varies"

def evaluate_strategy(leg_data):
    sorted_legs = sorted(leg_data, key=lambda x: (x[2], x[1]))
    strategy_type = "Complex Strategy"
    max_gain, max_loss = "Varies", "Varies"

    if len(sorted_legs) == 1:
        strategy_type, max_gain, max_loss = max_gain_loss_single_leg(sorted_legs[0])
    elif len(sorted_legs) == 2:
        strategy_type, max_gain, max_loss = max_gain_loss_two_legs(sorted_legs)
    elif len(sorted_legs) == 3:
        strategy_type, max_gain, max_loss = max_gain_loss_three_legs(sorted_legs)
    elif len(sorted_legs) == 4:
        strategy_type, max_gain, max_loss = max_gain_loss_four_legs(sorted_legs)
    else:
        strategy_type = "Complex Multi-Leg Strategy"

    return strategy_type, max_gain, max_loss

def plot_strategy(leg_data):
    prices = np.linspace(0, max(leg[2] for leg in leg_data) * 2, 500)
    total_pnl = np.zeros_like(prices)
   
    for leg in leg_data:
        pnl = [calculate_profit_loss(leg[0], leg[1], leg[2], leg[3], leg[4], leg[5], price) for price in prices]
        total_pnl += pnl

    plt.figure(figsize=(10, 5))
    plt.plot(prices, total_pnl, label='Total P/L')
    plt.axhline(0, color='black', linestyle='--')
    plt.xlabel('Stock Price at Expiration')
    plt.ylabel('Profit/Loss')
    plt.title('Profit/Loss Diagram')
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

def main():
    st.title("Dynamic Option Strategy Calculator")
    legs = st.number_input("Number of Legs", min_value=1, max_value=10, value=4, step=1)

    leg_data = []
    for i in range(legs):
        with st.expander(f"Leg {i+1}"):
            direction = st.selectbox("Client Direction", ["Client Buy", "Client Sell"], key=f"direction{i}")
            option_type = st.selectbox("Option Type", ["Call", "Put", "Stock"], key=f"option{i}")
            strike = st.number_input("Strike Price", value=100, key=f"strike{i}")
            premium = st.number_input("Premium", value=1.0, step=0.01, key=f"premium{i}")
            quantity = st.number_input("Quantity", value=1, min_value=1, key=f"quantity{i}")
            contract_size = st.number_input("Contract Size", value=100, min_value=1, key=f"contract_size{i}")
            leg_data.append((direction, option_type, strike, premium, quantity, contract_size))

    if st.button("Calculate"):
        strategy_type, max_gain, max_loss = evaluate_strategy(leg_data)
        st.write(f"Strategy Type: {strategy_type}")
        st.write(f"Maximum Gain: {max_gain}")
        st.write(f"Maximum Loss: {max_loss}")
        plot_strategy(leg_data)

if __name__ == "__main__":
    main()
