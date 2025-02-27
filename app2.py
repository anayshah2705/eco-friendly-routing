import streamlit as st
import openrouteservice
import folium
from web3 import Web3
import random
from streamlit_folium import folium_static

# Connect to Ganache
ganache_url = "HTTP://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))
assert web3.is_connected(), "⚠️ Web3 is not connected!"

# Smart contract details
contract_address = "0xA4F6B149052822539CF7D69a2751CF064eDea4b7"  # Replace with actual address
contract_abi = [
    {
        "inputs": [],
        "name": "fundContract",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "user",
                "type": "address"
            }
        ],
        "name": "giveReward",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,  # Fixed (false → False)
        "inputs": [
            {
                "indexed": True,  # Fixed (true → True)
                "internalType": "address",
                "name": "sender",
                "type": "address"
            },
            {
                "indexed": False,  # Fixed (false → False)
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "Funded",
        "type": "event"
    },
    {
        "anonymous": False,  # Fixed (false → False)
        "inputs": [
            {
                "indexed": True,  # Fixed (true → True)
                "internalType": "address",
                "name": "user",
                "type": "address"
            },
            {
                "indexed": False,  # Fixed (false → False)
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "RewardGiven",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "withdrawReward",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "stateMutability": "payable",
        "type": "receive"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "user",
                "type": "address"
            }
        ],
        "name": "checkReward",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getBalance",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "name": "rewards",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]  # Replace with your contract's actual ABI
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Mumbai locations
places = { 'Andheri': (19.1197, 72.8465),
    'Bandra': (19.059, 72.829),
    'Marine Drive': (18.9435, 72.8235),
    'Churchgate': (18.9353, 72.8277),
    'Bandra Kurla Complex': (19.0700, 72.8705),
    'Juhu': (19.1076, 72.8265),
    'Lower Parel': (18.9934, 72.8254),
    'Vashi': (19.0770, 72.9987),
    'Thane': (19.2183, 72.9781),
    'Dadar': (19.0186, 72.8300),
    'Powai': (19.1180, 72.9052),
    'Goregaon': (19.1551, 72.8494),
    'Worli': (18.9975, 72.8173),
    'Colaba': (18.9067, 72.8147),
    'Kurla': (19.0726, 72.8814)
    }  # Dictionary of locations with coordinates

# Simulated AQI and congestion data
aqi_data = {place: random.randint(50, 300) for place in places}
congestion_data = {place: random.randint(10, 100) for place in places}

# OpenRouteService API
API_KEY = "5b3ce3597851110001cf6248531a9782480a43888f5aa818a94ccc4a"
client = openrouteservice.Client(key=API_KEY)

# Streamlit UI
st.title("🌿 Eco-Friendly Route Finder")
source = st.selectbox("Select Source Location", list(places.keys()))
destination = st.selectbox("Select Destination Location", list(places.keys()))

if source and destination:
    preferences = ["recommended", "fastest", "shortest"]
    routes = []
    for pref in preferences:
        try:
            route = client.directions(
                coordinates=[places[source][::-1], places[destination][::-1]],
                profile='driving-car',
                format='geojson',
                preference=pref
            )
            routes.append((route, pref))
        except Exception as e:
            st.error(f"Error fetching {pref} route: {e}")

    # Calculate eco-score
    route_scores = []
    for route, pref in routes:
        avg_aqi = sum(aqi_data.values()) / len(places)
        avg_congestion = sum(congestion_data.values()) / len(places)
        eco_score = avg_aqi + avg_congestion  # Lower is better
        route_scores.append((route, eco_score, pref))
    
    route_scores.sort(key=lambda x: x[1])
    best_route, best_score, best_pref = route_scores[0]
    st.success(f"🌿 Recommended Eco-Friendly Route: {best_pref} (Score: {best_score})")
    
    # Map visualization
    mumbai_map = folium.Map(location=[19.0760, 72.8777], zoom_start=12)
    for route, _, pref in route_scores:
        folium.GeoJson(route, name=f'{pref.capitalize()} Route',
                       style_function=lambda _: {'color': 'blue', 'weight': 4}).add_to(mumbai_map)
    folium.GeoJson(best_route, name='Eco-Friendly Route',
                   style_function=lambda _: {'color': 'green', 'weight': 5}).add_to(mumbai_map)
    folium.Marker(places[source], popup=f"Start: {source}", icon=folium.Icon(color="red")).add_to(mumbai_map)
    folium.Marker(places[destination], popup=f"End: {destination}", icon=folium.Icon(color="blue")).add_to(mumbai_map)
    folium_static(mumbai_map)

    # Reward system
    if st.button("I took the eco-friendly route!"):
        user_wallet = st.text_input("Enter your Ethereum wallet address")
        if user_wallet:
            try:
                tx = contract.functions.giveReward(user_wallet).transact({'from': web3.eth.accounts[0]})
                web3.eth.wait_for_transaction_receipt(tx)
                st.success("✅ Reward given for choosing the eco-friendly route!")
            except Exception as e:
                st.error(f"⚠️ Error sending reward: {e}")
