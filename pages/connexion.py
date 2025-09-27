import dash
from dash import html, dcc, Output, Input, State, no_update
import pandas as pd
import os
import urllib.parse
from app_instance import app

CSV_FILE = "./data/infos_users.csv"

# --- Layout de la page de connexion / inscription ---
layout = html.Div([
    html.Div([
        # En-tête
        html.Div([
            html.H2("🎬 Connexion / Inscription", style={
                'fontSize': '2.5em',
                'fontWeight': '300',
                'marginBottom': '10px',
                'textShadow': '0 2px 4px rgba(0, 0, 0, 0.3)',
                'color': 'white'
            }),
            html.Div("Accédez à votre espace personnel d'annotation de films", style={
                'fontSize': '1.1em',
                'opacity': '0.9',
                'fontWeight': '300',
                'color': 'white'
            })
        ], style={
            'background': 'linear-gradient(45deg, #667eea, #764ba2)',
            'color': 'white',
            'textAlign': 'center',
            'padding': '30px'
        }),
        
        # Contenu principal
        html.Div([
            html.Div([
                html.Button("Connexion", id="btn-login", n_clicks=1, style={
                    'backgroundColor': '#667eea',
                    'color': 'white',
                    'border': 'none',
                    'padding': '12px 24px',
                    'borderRadius': '25px',
                    'fontSize': '1em',
                    'fontWeight': '500',
                    'marginRight': '15px',
                    'cursor': 'pointer',
                    'transition': 'all 0.3s ease',
                    'boxShadow': '0 4px 15px rgba(102, 126, 234, 0.3)'
                }),
                html.Button("Inscription", id="btn-register", n_clicks=0, style={
                    'backgroundColor': '#764ba2',
                    'color': 'white',
                    'border': 'none',
                    'padding': '12px 24px',
                    'borderRadius': '25px',
                    'fontSize': '1em',
                    'fontWeight': '500',
                    'cursor': 'pointer',
                    'transition': 'all 0.3s ease',
                    'boxShadow': '0 4px 15px rgba(118, 75, 162, 0.3)'
                })
            ], style={'textAlign': 'center', 'marginBottom': '30px'}),
            
            html.Div(id="tab-content"),
            html.Div(id="message", style={'textAlign': 'center', 'marginTop': '20px', 'fontSize': '1.1em'}),
        ], style={
            'padding': '40px',
            'backgroundColor': 'white'
        })
        
    ], style={
        'maxWidth': '500px',
        'margin': '0 auto',
        'background': 'rgba(255, 255, 255, 0.95)',
        'borderRadius': '15px',
        'boxShadow': '0 20px 40px rgba(0, 0, 0, 0.1)',
        'overflow': 'hidden'
    }),
    
    dcc.Store(id="user_id_store"),
    dcc.Store(id="selected_tab", data="login")
    
], style={
    'fontFamily': 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'minHeight': '100vh',
    'padding': '20px',
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'center'
})

# --- Changement d'onglet Connexion / Inscription ---
@app.callback(
    Output("selected_tab", "data"),
    Input("btn-login", "n_clicks"),
    Input("btn-register", "n_clicks"),
)
def switch_tab(n_login, n_register):
    if n_login > n_register:
        return "login"
    else:
        return "register"

# --- Contenu de l'onglet actif ---
@app.callback(
    Output("tab-content", "children"),
    Input("selected_tab", "data")
)
def render_tab(tab):
    return html.Div([
        html.Div([
            html.Label("Nom d'utilisateur", style={
                'display': 'block',
                'marginBottom': '8px',
                'fontWeight': '500',
                'color': '#333'
            }),
            dcc.Input(id="username", type="text", placeholder="Nom d'utilisateur", value="", style={
                'width': '100%',
                'padding': '15px',
                'border': '2px solid #e8e8e8',
                'borderRadius': '10px',
                'fontSize': '1em',
                'marginBottom': '20px',
                'transition': 'border-color 0.3s ease'
            })
        ]),
        html.Div([
            html.Label("Mot de passe", style={
                'display': 'block',
                'marginBottom': '8px',
                'fontWeight': '500',
                'color': '#333'
            }),
            dcc.Input(id="password", type="password", placeholder="Mot de passe", value="", style={
                'width': '100%',
                'padding': '15px',
                'border': '2px solid #e8e8e8',
                'borderRadius': '10px',
                'fontSize': '1em',
                'marginBottom': '30px',
                'transition': 'border-color 0.3s ease'
            })
        ]),
        html.Button("Se connecter" if tab == "login" else "S'inscrire", id="submit", n_clicks=0, style={
            'width': '100%',
            'padding': '15px',
            'backgroundColor': '#667eea',
            'color': 'white',
            'border': 'none',
            'borderRadius': '10px',
            'fontSize': '1.1em',
            'fontWeight': '600',
            'cursor': 'pointer',
            'transition': 'all 0.3s ease',
            'boxShadow': '0 4px 15px rgba(102, 126, 234, 0.3)'
        })
    ], style={'maxWidth': '300px', 'margin': '0 auto'})

# --- Gestion de la connexion / inscription ---
@app.callback(
    Output("url", "pathname"),
    Output("url", "search"),
    Output("message", "children"),
    Output("user_id_store", "data"),
    Input("submit", "n_clicks"),
    State("selected_tab", "data"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)

def handle_auth(n_clicks, tab, username, password):
    from dash import no_update
    import os
    import pandas as pd
    import urllib.parse
    import bcrypt

    if not username or not password:
        message = html.Div([
            "⚠️ Veuillez remplir tous les champs."
        ], style={
            'color': '#e74c3c',
            'backgroundColor': '#fdf2f2',
            'border': '1px solid #e74c3c',
            'borderRadius': '8px',
            'padding': '12px',
            'fontSize': '0.95em'
        })
        return no_update, no_update, message, None

    # Charger le CSV ou le créer s'il n'existe pas
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=["id", "username", "password"])
        df.to_csv(CSV_FILE, index=False)

    if tab == "login":
        user_row = df[df["username"] == username]
        if user_row.empty:
            message = html.Div([
                "❌ Pseudo ou mot de passe incorrect"
            ], style={
                'color': '#e74c3c',
                'backgroundColor': '#fdf2f2',
                'border': '1px solid #e74c3c',
                'borderRadius': '8px',
                'padding': '12px',
                'fontSize': '0.95em'
            })
            return no_update, no_update, message, None

        # Vérifier le mot de passe haché
        stored_hash = str(user_row.iloc[0]["password"]).encode('utf-8')
        if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            message = html.Div([
                "❌ Pseudo ou mot de passe incorrect"
            ], style={
                'color': '#e74c3c',
                'backgroundColor': '#fdf2f2',
                'border': '1px solid #e74c3c',
                'borderRadius': '8px',
                'padding': '12px',
                'fontSize': '0.95em'
            })
            return no_update, no_update, message, None

        # Connexion réussie
        pathname = "/main"
        search = f"?username={urllib.parse.quote(username)}"
        return pathname, search, "", int(user_row.iloc[0]["id"])

    else:  # register
        if username in df["username"].values:
            message = html.Div([
                "⚠️ Pseudo déjà utilisé"
            ], style={
                'color': '#f39c12',
                'backgroundColor': '#fefbf3',
                'border': '1px solid #f39c12',
                'borderRadius': '8px',
                'padding': '12px',
                'fontSize': '0.95em'
            })
            return no_update, no_update, message, None
        else:
            new_id = (df["id"].max() + 1) if not df.empty else 1

            # Hachage du mot de passe
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            hashed_password_str = hashed_password.decode('utf-8')

            new_row = pd.DataFrame([{
                "id": new_id,
                "username": username,
                "password": hashed_password_str
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)

            pathname = "/main"
            search = f"?username={urllib.parse.quote(username)}"
            return pathname, search, "", int(new_id)

