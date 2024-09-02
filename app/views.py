from app import app, db
from flask import render_template, request
import requests
import geopandas as gpd
import folium
from branca.colormap import LinearColormap
from app.models import WardPopulation, WardGeneralHealth, WardOccupation, WardTenures, WardVehicles
import plotly.express as px
import plotly.io as pio
import pandas as pd


def update_data():
    from app.utils import update_population_data, update_general_health_data, update_occupation_data, update_vehicle_availability_data, update_tenure_data
    update_population_data()
    update_general_health_data()
    update_occupation_data()
    update_vehicle_availability_data()
    update_tenure_data()

@app.route('/update_all', methods=['GET', 'POST'])
def update_all_data():
    update_data()
    return 'All data updated successfully!'

@app.route('/', methods=['GET', 'POST'])
@app.route('/wardprofile', methods=['GET', 'POST'])
def wardprofile():
    # Fetch GeoJSON data
    geo_json_url = (
        "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/WD_MAY_2023_UK_BGC/FeatureServer/0/query?"
        "where=LAD23NM%20%3D%20'LEWISHAM'&outFields=*&outSR=4326&f=geojson"
    )
    geo_json_data = requests.get(geo_json_url).json()

    # Fetch data from the database
    population_data = WardPopulation.query.all()
    health_data = WardGeneralHealth.query.all()
    occupation_data = WardOccupation.query.all()
    tenure_data = WardTenures.query.all()
    vehicle_data = WardVehicles.query.all()  # Fetch vehicle data

    # Map the data to ward codes
    population_map = {
        'total_population': {data.ward_code: data.total_population for data in population_data},
        'population_under_15': {data.ward_code: data.population_under_15 for data in population_data},
        'population_age_16_24': {data.ward_code: data.population_age_16_24 for data in population_data},
        'population_age_25_49': {data.ward_code: data.population_age_25_49 for data in population_data},
        'population_age_50_64': {data.ward_code: data.population_age_50_64 for data in population_data},
        'population_over_65': {data.ward_code: data.population_over_65 for data in population_data}
    }

    health_map = {
        'usual_residents': {data.ward_code: data.usual_residents for data in health_data},
        'residentsGoodHealth': {data.ward_code: data.residentsGoodHealth for data in health_data},
        'residentsFairHealth': {data.ward_code: data.residentsFairHealth for data in health_data},
        'residentsBadHealth': {data.ward_code: data.residentsBadHealth for data in health_data},
        'residentVeryBadHealth': {data.ward_code: data.residentVeryBadHealth for data in health_data}
    }

    occupation_map = {
        'managers_directors_senior_officials': {data.ward_code: data.managers_directors_senior_officials for data in occupation_data},
        'professional_occupations': {data.ward_code: data.professional_occupations for data in occupation_data},
        'associate_professional_technical': {data.ward_code: data.associate_professional_technical for data in occupation_data},
        'administrative_secretarial': {data.ward_code: data.administrative_secretarial for data in occupation_data},
        'skilled_trades': {data.ward_code: data.skilled_trades for data in occupation_data},
        'caring_leisure_service': {data.ward_code: data.caring_leisure_service for data in occupation_data},
        'sales_customer_service': {data.ward_code: data.sales_customer_service for data in occupation_data},
        'process_plant_machine_operatives': {data.ward_code: data.process_plant_machine_operatives for data in occupation_data},
        'elementary_occupations': {data.ward_code: data.elementary_occupations for data in occupation_data}
    }

    tenure_map = {
        'owns_outright': {data.ward_code: data.owns_outright for data in tenure_data},
        'owns_with_mortgage': {data.ward_code: data.owns_with_mortgage for data in tenure_data},
        'shared_ownership': {data.ward_code: data.shared_ownership for data in tenure_data},
        'rents_council': {data.ward_code: data.rents_council for data in tenure_data},
        'other_social_rented': {data.ward_code: data.other_social_rented for data in tenure_data},
        'rents_private_landlord': {data.ward_code: data.rents_private_landlord for data in tenure_data},
        'other_private_rented': {data.ward_code: data.other_private_rented for data in tenure_data},
        'lives_rent_free': {data.ward_code: data.lives_rent_free for data in tenure_data}
    }

    # Map the vehicle data to ward codes
    vehicle_map = {
        'no_cars_vans': {data.ward_code: data.no_cars_vans for data in vehicle_data},
        'one_car_van': {data.ward_code: data.one_car_van for data in vehicle_data},
        'two_cars_vans': {data.ward_code: data.two_cars_vans for data in vehicle_data},
        'three_or_more_cars_vans': {data.ward_code: data.three_or_more_cars_vans for data in vehicle_data},
    }

    # Determine the display type and category
    display_type = request.args.get('display', 'default')
    category = (
        request.args.get('age_category', 'total_population') if display_type == 'population' else
        request.args.get('health_category', 'usual_residents') if display_type == 'health' else
        request.args.get('occupation_category', 'managers_directors_senior_officials') if display_type == 'occupation' else
        request.args.get('tenure_category', 'owns_outright') if display_type == 'tenure' else
        request.args.get('vehicle_category', 'no_cars_vans') if display_type == 'vehicles' else
        'total_population'
    )

    # Determine the correct map based on display type
    data_map = {
        'population': population_map,
        'health': health_map,
        'occupation': occupation_map,
        'tenure': tenure_map,
        'vehicles': vehicle_map,
        'default': population_map  # Default to population_map
    }.get(display_type, population_map)  # Fallback to population_map if display_type is not recognized

    # Ensure category exists in the selected data_map
    if category not in data_map:
        category = 'no_cars_vans' if display_type == 'vehicles' else 'total_population'  # Fallback for vehicles

    # Calculate min and max values for the selected category in the GeoJSON data
    values = [data_map[category].get(feature['properties'].get('WD23CD', ''), 0.0) for feature in geo_json_data['features']]
    min_value = min(values, default=0)
    max_value = max(values, default=0)

    # Add selected data to the GeoJSON properties
    for feature in geo_json_data['features']:
        ward_code = feature['properties'].get('WD23CD', None)
        if ward_code:
            feature['properties']['data_value'] = data_map[category].get(ward_code, 0.0)

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(geo_json_data['features'])

    # Create a folium map
    m = folium.Map(location=[51.465, -0.02], zoom_start=12)

    # Define color scales for different display types
    color_scales = {
        'population': [
            (0, '#f7fcf5'), (0.5, '#74c476'), (1, '#00441b')
        ],
        'health': [
            (0, '#fee8c8'), (0.5, '#fdae61'), (1, '#a50034')
        ],
        'occupation': [
            (0, '#e7f3fe'), (0.5, '#2196f3'), (1, '#0d47a1')
        ],
        'tenure': [
            (0, '#f0f0f0'), (0.5, '#636363'), (1, '#252525')
        ],
        'vehicles': [
            (0, '#edf8e9'), (0.5, '#2ca25f'), (1, '#006d2c')
        ],
        'default': [
            (0, '#377eb8'), (0.5, '#4daf4a'), (1, '#ff7f00')
        ]
    }

    # Use the color scale based on the display type
    color_scale = LinearColormap(
        [color[1] for color in color_scales.get(display_type, color_scales['default'])], 
        vmin=min_value, vmax=max_value
    )

    if display_type in ['population', 'health', 'occupation', 'tenure', 'vehicles']:
        folium.GeoJson(
            geo_json_data,
            style_function=lambda feature: {
                'fillColor': color_scale(feature['properties'].get('data_value', 0)),
                'color': 'black',
                'weight': 1,
                'dashArray': '5, 5',
                'fillOpacity': 0.7,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['WD23NM', 'data_value'],
                aliases=['Ward Name:', category.replace("_", " ").title() + ": "],
                localize=True
            )
        ).add_to(m)

        color_scale.caption = category.replace("_", " ").title()
        color_scale.add_to(m)

        # Create a bar graph for the selected category
        df = pd.DataFrame([
            {
                'ward_name': data.ward_name,
                'value': getattr(data, category, 0),
                'category': category
            }
            for data in (population_data if display_type == 'population' else health_data if display_type == 'health' else occupation_data if display_type == 'occupation' else tenure_data if display_type == 'tenure' else vehicle_data)
        ])

        # Sort the DataFrame by ward_name alphabetically
        df = df.sort_values('ward_name')

        fig = px.bar(
            df[df['category'] == category],
            x='value',
            y='ward_name',
            color='value',
            color_continuous_scale=color_scales.get(display_type, color_scales['default']),  # Sequential color scale
            title=f'Ward {category.replace("_", " ").title()}',
            labels={'ward_name': 'Ward Name', 'value': category.replace("_", " ").title()},
            orientation='h'  # Horizontal bar chart
        )
        fig.update_layout(
            yaxis_title='Ward Name',
            xaxis_title=category.replace("_", " ").title(),
            autosize=True,
            height=600,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False, categoryorder="total ascending"),
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=False
        )
        fig.update_traces(marker_line_width=0)

        # Save figure to HTML
        graph_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

        # Create a table for the selected category
        table_html = df.to_html(classes="table table-striped", index=False)
            # Remove 'category' from the DataFrame before converting it to HTML
        table_html = df.drop(columns=['category'], errors='ignore').to_html(
        classes="table table-striped table-bordered table-hover", 
        index=False, 
        justify="center"
        )

    else:
        # Default view: ward colors
        colors = ['#377eb8', '#4daf4a', '#ff7f00', '#984ea3', '#e41a1c', '#ffff33', '#a65628', '#f781bf', '#999999']
        color_scale = LinearColormap(colors, vmin=0, vmax=len(gdf['WD23NM'].unique())).to_step(len(gdf['WD23NM'].unique()))

        ward_color_map = {name: color_scale(i) for i, name in enumerate(gdf['WD23NM'].unique())}

        folium.GeoJson(
            geo_json_data,
            style_function=lambda feature: {
                'fillColor': ward_color_map.get(feature['properties']['WD23NM'], '#000000'),
                'color': 'black',
                'weight': 1,
                'dashArray': '5, 5',
                'fillOpacity': 0.7,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['WD23NM'],
                aliases=['Ward Name:'],
                localize=True
            )
        ).add_to(m)

        color_scale.caption = 'Ward Colors'
        color_scale.add_to(m)

        graph_html = ''
        table_html = ''
    
    

    # Save map to HTML and pass to template
    map_html = m._repr_html_()
    return render_template('wardprofile.html', map_html=map_html, graph_html=graph_html, table_html=table_html)




