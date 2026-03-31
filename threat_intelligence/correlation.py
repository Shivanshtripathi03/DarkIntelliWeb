import networkx as nx
from database.db import db
from datetime import datetime

async def generate_threat_graph() -> dict:
    """
    Reads from database to build a NetworkX graph of relationships
    Returns it as a serialized nodelink format suitable for Plotly/D3
    """
    G = nx.Graph()
    
    cursor = db.threat_analysis.find().sort("timestamp", -1).limit(100)
    logs = await cursor.to_list(length=100)
    
    for log in logs:
        url = log['url']
        category = log['threat_category']
        
        # Add URL node
        if not G.has_node(url):
            G.add_node(url, type='url', label=url, category=category, risk=log['risk_score'])
            
        # Add category node
        if not G.has_node(category):
            G.add_node(category, type='category', label=category)
            
        # Link URL to Category
        G.add_edge(url, category)
        
        # Link mapped indicators
        for ind in log.get('extracted_indicators', []):
            ival = ind['value']
            itype = ind['type']
            
            if not G.has_node(ival):
                G.add_node(ival, type=itype, label=ival)
                
            G.add_edge(url, ival)

    data = nx.node_link_data(G)
    return data
