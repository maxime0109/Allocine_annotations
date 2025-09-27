import dash
from dash import html, dcc, dash_table, Output, Input, State, callback_context
import pandas as pd
import urllib.parse
from app_instance import app

layout = html.Div([
    dcc.Location(id='url-historique', refresh=False),
    html.Div(id='historique-content')
])

@app.callback(
    Output('historique-content', 'children'),
    Input('url-historique', 'search')
)
def update_historique_content(search):
    # Récupérer le username depuis l'URL
    username = None
    if search:
        params = urllib.parse.parse_qs(search.lstrip('?'))
        username = params.get('username', [''])[0]
    
    # Charger les fichiers CSV
    try:
        df = pd.read_csv('data/avis_user.csv', delimiter=';')
        df_films = pd.read_csv('data/avis_film_fr_sample.csv', delimiter=';')
        
        # Filtrer par utilisateur connecté
        if username:
            df_filtered = df[df['Username'] == username]
            titre_page = f"Historique des avis de {username}"
        else:
            df_filtered = pd.DataFrame(columns=df.columns if not df.empty else ["Username", "Code_Film", "Avis"])
            titre_page = "Historique des avis"
            
    except FileNotFoundError:
        df_filtered = pd.DataFrame(columns=["Username", "Code_Film", "Avis"])
        df_films = pd.DataFrame()
        titre_page = "Historique des avis"

    # --- Garder toutes les annotations distinctes par Film_ID ---
    # Plus de groupement par Code_Film, on affiche chaque Film_ID séparément

    # Créer les données et colonnes
    if not df_filtered.empty:
        # Créer des boutons cliquables pour chaque film
        film_buttons = []
        for idx, row in df_filtered.iterrows():
            film_code = row['Code_Film']
            avis = row['Avis']
            film_id = row.get('Film_ID', None)
            
            # Récupérer les 5 premiers mots de l'avis original
            review_preview = "Avis non trouvé"
            if film_id is not None and not df_films.empty:
                # Utiliser le Film_ID stocké directement
                film_review = df_films[df_films['Id'] == film_id]
                if not film_review.empty:
                    original_review = film_review.iloc[0]['review']
                    words = original_review.split()[:5]
                    review_preview = ' '.join(words) + '...' if len(original_review.split()) > 5 else original_review
                else:
                    # Si pas trouvé avec Film_ID, essayer avec le titre et Review_Index
                    film_title_matches = df_films[df_films['titre'] == film_code]
                    review_index = row.get('Review_Index', 0)
                    if not film_title_matches.empty and review_index < len(film_title_matches):
                        original_review = film_title_matches.iloc[review_index]['review']
                        words = original_review.split()[:5]
                        review_preview = ' '.join(words) + '...' if len(original_review.split()) > 5 else original_review
            
            # Couleur selon l'avis
            if avis == 'Positif':
                color = '#27ae60'
                emoji = '👍'
            elif avis == 'Negatif':
                color = '#e74c3c'
                emoji = '👎'
            else:  # Neutre
                color = '#95a5a6'
                emoji = '😐'
            
            film_buttons.append(
                html.Div([
                    dcc.Link([
                        html.Div([
                            html.Div([
                                html.Strong(f"{film_code} (ID: {film_id})", style={
                                    'fontSize': '1.1em',
                                    'color': '#333',
                                    'marginBottom': '5px',
                                    'display': 'block'
                                }),
                                html.Div([
                                    html.Span(emoji, style={'fontSize': '1.2em', 'marginRight': '8px'}),
                                    html.Span(avis, style={'color': color, 'fontWeight': '600'})
                                ]),
                                html.Div(f"Avis original: {review_preview}", style={
                                    'fontSize': '0.9em',
                                    'color': '#666',
                                    'fontStyle': 'italic',
                                    'marginTop': '8px',
                                    'paddingTop': '8px',
                                    'borderTop': '1px solid #f0f0f0'
                                })
                            ], style={'flex': '1'}),
                            html.Div("Cliquer pour revoir", style={
                                'fontSize': '0.8em',
                                'color': '#667eea',
                                'fontStyle': 'italic'
                            })
                        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start', 'width': '100%'})
                    ], href=f"/main?username={urllib.parse.quote(username)}&film={urllib.parse.quote(str(film_code))}&review_index={row.get('Review_Index', 0)}" if username else f"/main?film={urllib.parse.quote(str(film_code))}&review_index={row.get('Review_Index', 0)}",
                       style={'display': 'block', 'textDecoration': 'none', 'color': 'inherit'})
                ], style={'backgroundColor': 'white','border': '1px solid #e8e8e8','borderRadius': '10px',
                          'padding': '15px 20px','marginBottom': '10px','boxShadow': '0 2px 8px rgba(0, 0, 0, 0.05)',
                          'transition': 'all 0.3s ease','cursor': 'pointer'})
            )
        
        table_component = html.Div(film_buttons, style={'maxHeight': '600px','overflowY': 'auto','padding': '10px 0'})
    else:
        # Message si pas de données
        table_component = html.Div([
            html.P("Aucun avis trouvé pour cet utilisateur.", style={'textAlign': 'center','fontSize': '1.2em','color': '#666','padding': '40px'})
        ])
    
    return html.Div([
        # Container principal avec style moderne
        html.Div([
            # En-tête
            html.Div([
                html.H2("📽️ " + titre_page, style={'fontSize': '2.5em','fontWeight': '300','marginBottom': '10px','textShadow': '0 2px 4px rgba(0, 0, 0, 0.3)','color': 'white'}),
                html.Div("Cliquez sur un film pour le revoir et changer votre avis", style={'fontSize': '1.1em','opacity': '0.9','fontWeight': '300','color': 'white'})
            ], style={'background': 'linear-gradient(45deg, #667eea, #764ba2)','color': 'white','textAlign': 'center','padding': '30px'}),
            
            # Container du contenu
            html.Div([table_component], style={'padding': '30px','backgroundColor': '#f8f9ff'}),
            
            # Barre de statistiques
            html.Div([
                html.Strong(f"{len(df_filtered)}", style={'color': '#667eea'}),
                html.Span(" avis au total • Cliquez sur un film pour le revoir")
            ], style={'background': '#f8f9ff','padding': '15px 30px','borderTop': '1px solid #e8e8e8','color': '#666','fontSize': '0.9em','textAlign': 'center'}),
            
            # Bouton retour
            html.Div([dcc.Link('Retour au menu principal', href=f"/main?username={urllib.parse.quote(username)}" if username else "/main",
                               style={'display': 'inline-block','padding': '12px 24px','backgroundColor': '#667eea','color': 'white','textDecoration': 'none','borderRadius': '25px','fontSize': '0.9em','fontWeight': '500','transition': 'all 0.3s ease','boxShadow': '0 4px 15px rgba(102, 126, 234, 0.3)'})
                        ], style={'textAlign': 'center','padding': '20px','backgroundColor': 'white'})
            
        ], style={'maxWidth': '1200px','margin': '0 auto','background': 'rgba(255, 255, 255, 0.95)','borderRadius': '15px','boxShadow': '0 20px 40px rgba(0, 0, 0, 0.1)','overflow': 'hidden'})
        
    ], style={'fontFamily': 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif','background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)','minHeight': '100vh','padding': '20px'})
