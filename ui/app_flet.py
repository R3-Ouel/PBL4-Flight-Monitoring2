from flet import *
import pandas as pd
import plotly.graph_objects as go
import flet_charts as fch  # Ta lib pour Plotly


async def main(page: Page):
    # --- 1. CONFIGURATION DE LA PAGE ---
    page.title = "FDMS - Mission Control"
    page.bgcolor = "#050505" 
    page.padding = 20
    page.theme_mode = ThemeMode.DARK
    page.window_maximized = True # On ouvre en grand pour le style

    # --- 2. CHARGEMENT DES DONNÉES ---
    try:
        # Note : On s'assure que le CSV est bien lu
        df = pd.read_csv("flight_data.csv")
        df = df.astype({'timestamp': float, 
                'altitude': float, 
                'vitesse': float, 
                'ax': float, 
                'ay': float, 
                'az': float, 
                'roll': float, 
                'pitch': float, 
                'yaw': float}) # Convertit les données en float pour éviter les problèmes de type dans Plotly
    except Exception as e:
        print(f"Erreur : {e}")
        page.add(Text("Fichier CSV introuvable. Lance le simulateur d'abord !", color="red"))
        return

    # --- 3. FONCTION USINE À GRAPHIQUES ---
    def create_neon_chart(df: pd.DataFrame, y_cols: list | str, title: str, colors: list | str) -> Container:
        fig = go.Figure()
        
        if isinstance(y_cols, str):
            y_cols = [y_cols]
        if isinstance(colors, str):
            colors = [colors]
            
        # Add empty traces for animation start
        for col, color in zip(y_cols, colors):
            fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name=col, line=dict(color=color, width=3)))
            
        # Create frames for animation
        frames = []
        step = max(1, len(df) // 50)  # 50 frames for smooth animation
        for i in range(0, len(df), step):
            frame_data = []
            for col, color in zip(y_cols, colors):
                frame_data.append(go.Scatter(
                    x=df["timestamp"][:i+1], 
                    y=df[col][:i+1], 
                    mode='lines',
                    name=col,
                    line=dict(color=color, width=3)
                ))
            frames.append(go.Frame(data=frame_data, name=str(i)))
        
        # Add final frame with full data
        final_data = []
        for col, color in zip(y_cols, colors):
            final_data.append(go.Scatter(
                x=df["timestamp"], 
                y=df[col], 
                mode='lines',
                name=col,
                line=dict(color=color, width=3)
            ))
        frames.append(go.Frame(data=final_data, name='end'))
        
        fig.frames = frames
            
        fig.update_layout(
            title=title,
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=colors[0], family="Courier New"),
            margin=dict(l=10, r=10, t=40, b=10),
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                buttons=[dict(label="Play",
                              method="animate",
                              args=[None, dict(frame=dict(duration=50, redraw=False), fromcurrent=True, mode='immediate')])]
            )],
            sliders=[dict(
                active=0,
                steps=[dict(method="animate", args=[[f.name], dict(mode="immediate", frame=dict(duration=50, redraw=False), transition=dict(duration=0))]) for f in fig.frames],
                currentvalue={"prefix": "Frame:"},
            )]
        )
        
        return Container(
            content=fch.PlotlyChart(figure=fig, expand=True),
            border=Border.all(1, "#222222"),
            border_radius=10,
            padding=10,
            bgcolor="#111111",
            opacity=0,  # Start invisible for fade-in animation
            expand=True
        )

    def create_mapbox_chart(df: pd.DataFrame) -> Container:
        # Check if lat/lon exist, otherwise create dummy data for demonstration
        if 'latitude' not in df.columns:
            df['latitude'] = 48.8566 + (df['timestamp'] * 0.0001)
        if 'longitude' not in df.columns:
            df['longitude'] = 2.3522 + (df['timestamp'] * 0.0001)

        fig = go.Figure()
        
        # Add empty trace for animation start
        fig.add_trace(go.Scattermapbox(
            lat=[],
            lon=[],
            mode='markers',
            marker=dict(size=10, color='#FFA500', opacity=0.8),
            name="Trajectoire GPS"
        ))

        # Create frames for animation
        frames = []
        step = max(1, len(df) // 50)
        for i in range(0, len(df), step):
            frames.append(go.Frame(data=[go.Scattermapbox(
                lat=df['latitude'][:i+1],
                lon=df['longitude'][:i+1],
                mode='markers',
                marker=dict(size=10, color='#FFA500', opacity=0.8),
                name="Trajectoire GPS"
            )], name=str(i)))
        
        # Add final frame
        frames.append(go.Frame(data=[go.Scattermapbox(
            lat=df['latitude'],
            lon=df['longitude'],
            mode='markers',
            marker=dict(size=10, color='#FFA500', opacity=0.8),
            name="Trajectoire GPS"
        )], name='end'))
        
        fig.frames = frames

        fig.update_layout(
            mapbox_style="carto-darkmatter",
            mapbox=dict(
                center=dict(lat=20, lon=0), # Centré pour voir le monde entier
                zoom=1.2 # Dézoomé pour ressembler à la carte du monde
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0), # Pas de marge pour que ça prenne tout l'espace comme une bannière
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                buttons=[dict(label="Play",
                              method="animate",
                              args=[None, dict(frame=dict(duration=50, redraw=False), fromcurrent=True, mode='immediate')])]
            )],
            sliders=[dict(
                active=0,
                steps=[dict(method="animate", args=[[f.name], dict(mode="immediate", frame=dict(duration=50, redraw=False), transition=dict(duration=0))]) for f in fig.frames],
                currentvalue={"prefix": "Frame:"},
            )]
        )

        return Container(
            content=fch.PlotlyChart(figure=fig, expand=True),
            border=Border.all(1, "#222222"),
            border_radius=10,
            padding=0, # On réduit le padding pour maximiser la carte
            bgcolor="#111111",
            opacity=0,  # Start invisible for fade-in animation
        )

    # Génération des composants
    chart_gps = create_mapbox_chart(df)
    chart_alt = create_neon_chart(df, "altitude", "ALTITUDE (m)", "#00FFFF")
    chart_vit = create_neon_chart(df, "vitesse", "VITESSE (m/s)", "#FF00FF")
    chart_acc = create_neon_chart(df, "az", "ACCEL Z (G)", "#39FF14")

    # Attitude : Roll, Pitch, Yaw (Jaune, Orange, Blanc)
    chart_att = create_neon_chart(df, ["roll", "pitch", "yaw"], "ATTITUDE (deg)", ["#FFD700", "#FF8C00", "#FFFFFF"])

    # --- 4. MISE EN PAGE FINALE ---
    page.add(
        # Header
        Row([
            Text("DRONE FLIGHT MONITORING SYSTEM", size=30, weight="bold", color="#00FFFF"),
            Text("LIVE TELEMETRY", color="#39FF14", italic=True)
        ], alignment=MainAxisAlignment.SPACE_BETWEEN),
        
        Divider(color="#222222", height=20),

        # Grille de graphiques (Le Dashboard)
        ResponsiveRow([
            # Ligne 1 (GPS - Bandeau horizontal comme dans inspi1)
            Column([chart_gps], col={"sm": 12, "md": 12}, height=250),
            
            # Ligne 2
            Column([chart_alt], col={"sm": 12, "md": 6}, height=190),
            Column([chart_vit], col={"sm": 12, "md": 6}, height=190),
            
            # Ligne 3
            Column([chart_acc], col={"sm": 12, "md": 6}, height=190),
            Column([chart_att], col={"sm": 12, "md": 6}, height=190),
            Column([Text("© 2024 FDMS - All rights reserved", color="#222222")], col={"sm": 12}, alignment=MainAxisAlignment.CENTER) # Footer
        ], spacing=20, run_spacing=20)
    )

    # Animate charts fade-in
    import asyncio
    await asyncio.sleep(0.5)
    for chart in [chart_gps, chart_alt, chart_vit, chart_acc, chart_att]:
        chart.animate_opacity = 2000
        chart.animate_opacity_curve = AnimationCurve.EASE_IN_OUT
        chart.opacity = 1
    page.update()

if __name__ == "__main__":
    app(main)