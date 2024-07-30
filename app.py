import streamlit as st
import numpy as np
import plotly.graph_objects as go

def calculate_pnl(expiration_price, legs, contract_size):
    pnl = 0
    for leg in legs:
        direction = leg['direction']
        option_type = leg['option_type']
        strike_price = leg['strike_price']
        premium = leg['premium']
        quantity = leg['quantity'] * contract_size

        if option_type == 'call':
            if direction == 'client buy':
                pnl += quantity * (max(0, expiration_price - strike_price) - premium)
            else:
                pnl += quantity * (premium - max(0, expiration_price - strike_price))
        else:  # put option
            if direction == 'client buy':
                pnl += quantity * (max(0, strike_price - expiration_price) - premium)
            else:
                pnl += quantity * (premium - max(0, strike_price - expiration_price))

    return pnl

def identify_strategy(legs):
    # Strategy identification logic
    return 'Complex Strategy'

def calculate_max_gain_loss(legs, contract_size):
    min_price = min(leg['strike_price'] for leg in legs)
    max_price = max(leg['strike_price'] for leg in legs)
    test_prices = np.linspace(min_price - 20, max_price + 20, 500)
    
    pnls = [calculate_pnl(price, legs, contract_size) for price in test_prices]
    max_gain = max(pnls)
    max_loss = min(pnls)
    
    return max_gain, max_loss, test_prices, pnls

def plot_payoff_chart(legs, contract_size, test_prices, pnls):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=test_prices, y=pnls, mode='lines', name='Payoff'))

    for leg in legs:
        fig.add_vline(x=leg['strike_price'], line=dict(color='red', dash='dash'), name=f'Strike Price {leg["strike_price"]}')

    fig.update_layout(
        title='Option Strategy Payoff Chart',
        xaxis_title='Expiration Price',
        yaxis_title='P&L',
        showlegend=False
    )

    st.plotly_chart(fig)

st.title('Dynamic Options Strategy Calculator')

num_legs = st.number_input('Enter Number of Legs', min_value=1, max_value=10, value=1)

legs = []
for i in range(num_legs):
    st.write(f'Leg {i + 1}')
    direction = st.selectbox(f'Direction for Leg {i + 1}', ['client buy', 'client sell'], key=f'direction_{i}')
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

contract_size = st.number_input('Enter Contract Size', value=100)

if st.button('Calculate Maximum Gain and Loss'):
    max_gain, max_loss, test_prices, pnls = calculate_max_gain_loss(legs, contract_size)
    
    st.write(f'Strategy: {identify_strategy(legs)}')

    if isinstance(max_gain, str):
        st.write(f'Maximum Gain: {max_gain}')
    else:
        st.write(f'Maximum Gain: {max_gain:.2f}')
    
    if isinstance(max_loss, str):
        st.write(f'Maximum Loss: {max_loss}')
    else:
        st.write(f'Maximum Loss: {max_loss:.2f}')
    
    plot_payoff_chart(legs, contract_size, test_prices, pnls)

    # Detailed calculations for each leg
    with st.expander("Details for Each Leg"):
        for i, leg in enumerate(legs):
            st.write(f"Leg {i + 1}")
            st.write(f"Direction: {leg['direction']}")
            st.write(f"Option Type: {leg['option_type']}")
            st.write(f"Strike Price: {leg['strike_price']}")
            st.write(f"Premium: {leg['premium']}")
            st.write(f"Quantity: {leg['quantity']}")

expiration_price_input = st.number_input('Enter Specific Expiration Price', value=100.0)
pnl_at_expiration = calculate_pnl(expiration_price_input, legs, contract_size)
st.write(f'Gain/Loss at Given Expiration Price: {pnl_at_expiration:.2f}')
