import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def calculate_pnl(expiration_price, legs, contract_size):
    pnl = 0
    for leg in legs:
        direction = leg['direction']
        option_type = leg['option_type']
        strike_price = leg['strike_price']
        premium = leg['premium']
        quantity = leg['quantity']
       
        if option_type == 'call':
            if direction == 'buy':
                pnl += max(0, expiration_price - strike_price) * quantity * contract_size - premium * quantity * contract_size
            else:
                pnl += premium * quantity * contract_size - max(0, expiration_price - strike_price) * quantity * contract_size
        else:  # put option
            if direction == 'buy':
                pnl += max(0, strike_price - expiration_price) * quantity * contract_size - premium * quantity * contract_size
            else:
                pnl += premium * quantity * contract_size - max(0, strike_price - expiration_price) * quantity * contract_size

    return pnl

def calculate_single_leg_gain_loss(leg, contract_size):
    direction = leg['direction']
    option_type = leg['option_type']
    strike_price = leg['strike_price']
    premium = leg['premium']
    quantity = leg['quantity']

    if option_type == 'call':
        if direction == 'buy':
            max_gain = 'Unlimited'
            max_loss = premium * quantity * contract_size
        else:
            max_gain = premium * quantity * contract_size
            max_loss = 'Unlimited'
    else:  # put option
        if direction == 'buy':
            max_gain = (strike_price - premium) * quantity * contract_size
            max_loss = premium * quantity * contract_size
        else:
            max_gain = premium * quantity * contract_size
            max_loss = (strike_price - premium) * quantity * contract_size

    return max_gain, max_loss

def calculate_two_leg_gain_loss(legs, contract_size):
    expiration_prices = np.linspace(0, 2 * max(leg['strike_price'] for leg in legs), 1000)
    pnl = [calculate_pnl(price, legs, contract_size) for price in expiration_prices]

    max_gain = max(pnl)
    max_loss = min(pnl)
   
    return max_gain, max_loss

def calculate_max_gain_loss(legs, contract_size):
    if len(legs) == 1:
        return calculate_single_leg_gain_loss(legs[0], contract_size)
    elif len(legs) == 2:
        return calculate_two_leg_gain_loss(legs, contract_size)
    # Add more elif blocks for 3, 4, ... 10 legs as needed
    else:
        expiration_prices = np.linspace(0, 2 * max(leg['strike_price'] for leg in legs), 1000)
        pnl = [calculate_pnl(price, legs, contract_size) for price in expiration_prices]
       
        max_gain = max(pnl)
        max_loss = min(pnl)

    return max_gain, max_loss

def plot_payoff_chart(legs, contract_size):
    expiration_prices = np.linspace(0, 2 * max(leg['strike_price'] for leg in legs), 500)
    pnl = [calculate_pnl(price, legs, contract_size) for price in expiration_prices]

    plt.figure(figsize=(10, 6))
    plt.plot(expiration_prices, pnl, label='Payoff')
    plt.axhline(0, color='black', linewidth=0.5)
    for leg in legs:
        plt.axvline(leg['strike_price'], color='red', linestyle='--', label=f'Strike Price {leg["strike_price"]}')
    plt.xlabel('Expiration Price')
    plt.ylabel('P&L')
    plt.title('Option Strategy Payoff Chart')
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

st.title('Dynamic Options Strategy Calculator')

num_legs = st.number_input('Enter Number of Legs', min_value=1, max_value=10, value=1)

legs = []
for i in range(num_legs):
    st.write(f'Leg {i + 1}')
    direction = st.selectbox(f'Direction for Leg {i + 1}', ['buy', 'sell'], key=f'direction_{i}')
    option_type = st.selectbox(f'Option Type for Leg {i + 1}', ['call', 'put'], key=f'option_type_{i}')
    strike_price = st.number_input(f'Strike Price for Leg {i + 1}', value=100.0, key=f'strike_price_{i}')
    premium = st.number_input(f'Premium for Leg {i + 1}', value=1.0, key=f'premium_{i}')
    quantity = st.number_input(f'Quantity for Leg {i + 1}', value=1, key=f'quantity_{i}')
   
    legs.append({
        'direction': direction,
        'option_type': option_type,
        'strike_price': strike_price,
        'premium': premium,
        'quantity': quantity
    })

contract_size = st.number_input('Enter Contract Size', value=1)

if st.button('Calculate Maximum Gain and Loss'):
    max_gain, max_loss = calculate_max_gain_loss(legs, contract_size)
   
    if max_gain == 'Unlimited':
        st.write('Maximum Gain: Unlimited')
    else:
        st.write(f'Maximum Gain: {max_gain:.2f}')
   
    if max_loss == 'Unlimited':
        st.write('Maximum Loss: Unlimited')
    else:
        st.write(f'Maximum Loss: {max_loss:.2f}')
   
    plot_payoff_chart(legs, contract_size)
