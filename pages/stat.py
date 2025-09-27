from dash import html, dcc
import pandas as pd
import plotly.express as px
import os
import urllib.parse

CSV_FILE = "./data/avis_user.csv"
FILM_FILE = "./data/avis_film_fr_sample.csv"

def layout(search=None):
    # Récupérer le username depuis l'URL
    params = urllib.parse.parse_qs(search[1:]) if search else {}
    username = params.get('username', [None])[0]

    # Charger les films et les avis
    df_films = pd.read_csv(FILM_FILE, delimiter=';')
    
    if os.path.exists(CSV_FILE):
        df_avis = pd.read_csv(CSV_FILE, delimiter=';')
        # Nettoyage pour éviter les espaces dans les valeurs
        for col in ['Username', 'Code_Film', 'Avis']:
            if col in df_avis.columns:
                df_avis[col] = df_avis[col].astype(str).str.strip()
    else:
        df_avis = pd.DataFrame(columns=["Username", "Code_Film", "Avis"])

    if username:
        df_user = df_avis[df_avis['Username'] == username]
    else:
        df_user = pd.DataFrame(columns=["Username", "Code_Film", "Avis"])

    # --- Graphique 1 : films notés vs restant ---
    films_notes = df_user['Code_Film'].nunique() if not df_user.empty else 0
    films_total = df_films.shape[0]
    films_restant = max(films_total - films_notes, 0)

    df_camebert1 = pd.DataFrame({
        'Statut': ['Notés', 'Restants'],
        'Nombre': [films_notes, films_restant]
    })

    fig1 = px.pie(df_camebert1, values='Nombre', names='Statut', title='Films notés / Restants')
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Segoe UI, sans-serif", size=12),
        title_font=dict(size=18, color='#333'),
        margin=dict(t=50, b=20, l=20, r=20)
    )

    # --- Graphique 2 : avis positifs vs négatifs ---
    if not df_user.empty and 'Avis' in df_user.columns:
        nb_positif = (df_user['Avis'] == 'Positif').sum()
        nb_negatif = (df_user['Avis'] == 'Negatif').sum()
    else:
        nb_positif = 0
        nb_negatif = 0

    df_camebert2 = pd.DataFrame({
        'Avis': ['Positif', 'Negatif'],
        'Nombre': [nb_positif, nb_negatif]
    })

    fig2 = px.pie(df_camebert2, values='Nombre', names='Avis', title='Avis positifs / négatifs')
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Segoe UI, sans-serif", size=12),
        title_font=dict(size=18, color='#333'),
        margin=dict(t=50, b=20, l=20, r=20)
    )

    # --- Layout de la page ---
    return html.Div([
        html.Div([
            # En-tête
            html.Div([
                html.H2(f"📊 Statistiques de {username}" if username else "📊 Statistiques", style={
                    'fontSize': '2.5em',
                    'fontWeight': '300',
                    'marginBottom': '10px',
                    'textShadow': '0 2px 4px rgba(0, 0, 0, 0.3)',
                    'color': 'white'
                }),
                html.Div("Analysez vos habitudes d'annotation de films", style={
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
            
            # Statistiques rapides
            html.Div([
                html.Div([
                    html.H3(f"{films_notes}", style={
                        'fontSize': '2.5em',
                        'margin': '0',
                        'color': '#667eea'
                    }),
                    html.P("Films notés", style={'fontSize': '1.1em','margin': '5px 0 0 0','color': '#666'})
                ], style={'textAlign': 'center','backgroundColor': 'white','padding': '25px',
                          'borderRadius': '15px','boxShadow': '0 4px 15px rgba(0, 0, 0, 0.1)','margin': '10px'}),
                
                html.Div([
                    html.H3(f"{nb_positif + nb_negatif}", style={'fontSize': '2.5em','margin': '0','color': '#27ae60'}),
                    html.P("Avis donnés", style={'fontSize': '1.1em','margin': '5px 0 0 0','color': '#666'})
                ], style={'textAlign': 'center','backgroundColor': 'white','padding': '25px',
                          'borderRadius': '15px','boxShadow': '0 4px 15px rgba(0, 0, 0, 0.1)','margin': '10px'}),
                
                html.Div([
                    html.H3(f"{films_restant}", style={'fontSize': '2.5em','margin': '0','color': '#f39c12'}),
                    html.P("Films restants", style={'fontSize': '1.1em','margin': '5px 0 0 0','color': '#666'})
                ], style={'textAlign': 'center','backgroundColor': 'white','padding': '25px',
                          'borderRadius': '15px','boxShadow': '0 4px 15px rgba(0, 0, 0, 0.1)','margin': '10px'})
            ], style={'display': 'flex','justifyContent': 'space-around','flexWrap': 'wrap','padding': '30px 20px',
                      'backgroundColor': '#f8f9ff'}),
            
             # Graphiques
            html.Div([
                html.Div([dcc.Graph(figure=fig1)], style={'backgroundColor': 'white','borderRadius': '15px',
                                                         'boxShadow': '0 4px 15px rgba(0, 0, 0, 0.1)',
                                                         'margin': '10px','padding': '20px','flex': '1','minWidth': '400px'}),
                html.Div([dcc.Graph(figure=fig2)], style={'backgroundColor': 'white','borderRadius': '15px',
                                                         'boxShadow': '0 4px 15px rgba(0, 0, 0, 0.1)',
                                                         'margin': '10px','padding': '20px','flex': '1','minWidth': '400px'})
            ], style={'display': 'flex','justifyContent': 'space-around','flexWrap': 'wrap','padding': '20px','backgroundColor': 'white'}),

            # --- Dropdowns et graphique filtré ---
            html.Div([
                html.Div([
                    html.Label("Sélectionner un film noté :", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='dropdown-film',
                        options=[
                            {'label': film, 'value': film}
                            for film in sorted(df_avis['Code_Film'].unique())
                        ],
                        value=None,
                        placeholder="Choisir un film...",
                        style={'marginBottom': '15px'}
                    ),
                ], style={'flex': '1', 'minWidth': '300px', 'marginRight': '20px'}),

                html.Div([
                    html.Label("Sélectionner un utilisateur :", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='dropdown-user',
                        options=([{'label': 'Tous', 'value': 'Tous'}] +
                                 [{'label': user, 'value': user}
                                  for user in sorted(df_avis['Username'].unique())]),
                        value='Tous',
                        placeholder="Choisir un utilisateur...",
                        style={'marginBottom': '15px'}
                    ),
                ], style={'flex': '1', 'minWidth': '300px'}),

            ], style={'display': 'flex', 'justifyContent': 'center', 'padding': '20px', 'backgroundColor': 'white'}),

            html.Div([
                dcc.Graph(id='graph-avis-film')
            ], style={'backgroundColor': 'white','borderRadius': '15px',
                      'boxShadow': '0 4px 15px rgba(0, 0, 0, 0.1)',
                      'margin': '10px','padding': '20px','maxWidth': '600px','marginLeft': 'auto','marginRight': 'auto'}),
            
            # Bouton retour
            html.Div([
                dcc.Link('Retour au menu principal',
                         href=f"/main?username={urllib.parse.quote(username)}" if username else '/connexion',
                         style={'display': 'inline-block','padding': '12px 24px','backgroundColor': '#667eea',
                                'color': 'white','textDecoration': 'none','borderRadius': '25px','fontSize': '0.9em',
                                'fontWeight': '500','transition': 'all 0.3s ease','boxShadow': '0 4px 15px rgba(102, 126, 234, 0.3)'}
                         )
            ], style={'textAlign': 'center','padding': '20px','backgroundColor': 'white'})
            
        ], style={'maxWidth': '1200px','margin': '0 auto','background': 'rgba(255, 255, 255, 0.95)',
                  'borderRadius': '15px','boxShadow': '0 20px 40px rgba(0, 0, 0, 0.1)','overflow': 'hidden'})
        
    ], style={'fontFamily': 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
              'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)','minHeight': '100vh','padding': '20px'})
