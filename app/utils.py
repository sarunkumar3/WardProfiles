import json
import logging
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.models import WardPopulation, WardGeneralHealth, WardOccupation, WardVehicles, WardTenures

# Set up logging
logging.basicConfig(level=logging.INFO)

def update_general_health_data():
    file_path = 'app/static/json/general_health/general_health.json'  # Path to your JSON file

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        if 'obs' not in data:
            raise ValueError("Invalid data structure in general health JSON file")

        # Initialize a dictionary to hold data for each ward
        all_data = {}

        # Parse the response to extract relevant information
        for item in data['obs']:
            ward_code = item['geography']['geogcode']
            ward_name = item['geography']['description']
            health_category = item['c2021_health_6']['description']
            value = item['obs_value']['value']

            # Initialize the ward data if not already done
            if ward_code not in all_data:
                all_data[ward_code] = {
                    'ward_name': ward_name,
                    'usual_residents': 0,
                    'residentsGoodHealth': 0,
                    'residentsFairHealth': 0,
                    'residentsBadHealth': 0,
                    'residentVeryBadHealth': 0
                }

            # Map health category to the correct field in the dictionary
            if health_category == 'Total: All usual residents':
                all_data[ward_code]['usual_residents'] = value
            elif health_category == 'Very good health' or health_category == 'Good health':
                all_data[ward_code]['residentsGoodHealth'] += value
            elif health_category == 'Fair health':
                all_data[ward_code]['residentsFairHealth'] = value
            elif health_category == 'Bad health':
                all_data[ward_code]['residentsBadHealth'] = value
            elif health_category == 'Very bad health':
                all_data[ward_code]['residentVeryBadHealth'] = value

        # Update or insert the data into the database
        for ward_code, data in all_data.items():
            existing_record = WardGeneralHealth.query.filter_by(ward_code=ward_code).first()
            if existing_record:
                existing_record.usual_residents = data['usual_residents']
                existing_record.residentsGoodHealth = data['residentsGoodHealth']
                existing_record.residentsFairHealth = data['residentsFairHealth']
                existing_record.residentsBadHealth = data['residentsBadHealth']
                existing_record.residentVeryBadHealth = data['residentVeryBadHealth']
                # logging.info(f"Updated existing health record for ward {ward_code}")
            else:
                new_record = WardGeneralHealth(
                    ward_code=ward_code,
                    ward_name=data['ward_name'],
                    usual_residents=data['usual_residents'],
                    residentsGoodHealth=data['residentsGoodHealth'],
                    residentsFairHealth=data['residentsFairHealth'],
                    residentsBadHealth=data['residentsBadHealth'],
                    residentVeryBadHealth=data['residentVeryBadHealth']
                )
                db.session.add(new_record)
                # logging.info(f"Added new health record for ward {ward_code}")

        # Commit the changes to the database
        db.session.commit()
        # logging.info("General health data updated successfully.")

    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON in file: {file_path}")
    except ValueError as ve:
        logging.error(ve)
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


def update_population_data():
    try:
        # Define file paths for different population categories
        file_paths = {
            'total_population': 'app/static/json/population/total_population.json',
            'population_under_15': 'app/static/json/population/population_under_15.json',
            'population_16_24': 'app/static/json/population/population_16_24.json',
            'population_25_49': 'app/static/json/population/population_25_49.json',
            'population_50_64': 'app/static/json/population/population_50_64.json',
            'population_over_65': 'app/static/json/population/population_over_65.json'
        }

        # Initialize a dictionary to hold data for all categories
        all_data = {}

        # Load data from JSON files
        for category, file_path in file_paths.items():
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)

                # Check if data contains 'obs' key
                if 'obs' not in data:
                    raise ValueError(f"Invalid data structure in {category} JSON file")

                # Parse the response to extract relevant information
                for item in data['obs']:
                    ward_code = item['geography']['geogcode']
                    ward_name = item['geography']['description']
                    value = item['obs_value']['value']

                    # Initialize the ward data if not already done
                    if ward_code not in all_data:
                        all_data[ward_code] = {
                            'ward_name': ward_name,
                            'total_population': 0,
                            'population_under_15': 0,
                            'population_16_24': 0,
                            'population_25_49': 0,
                            'population_50_64': 0,
                            'population_over_65': 0
                        }

                    # Update the ward data with the value from the current category
                    all_data[ward_code][category] = value

            except FileNotFoundError:
                logging.error(f"File not found: {file_path}")
                continue
            except json.JSONDecodeError:
                logging.error(f"Error decoding JSON in file: {file_path}")
                continue
            except ValueError as ve:
                logging.error(ve)
                continue

        # Update or insert the data into the database
        for ward_code, data in all_data.items():
            existing_record = WardPopulation.query.filter_by(ward_code=ward_code).first()
            if existing_record:
                existing_record.total_population = data['total_population']
                existing_record.population_under_15 = data['population_under_15']
                existing_record.population_age_16_24 = data['population_16_24']
                existing_record.population_age_25_49 = data['population_25_49']
                existing_record.population_age_50_64 = data['population_50_64']
                existing_record.population_over_65 = data['population_over_65']
                # logging.info(f"Updated existing record for ward {ward_code}")
            else:
                new_record = WardPopulation(
                    ward_code=ward_code,
                    ward_name=data['ward_name'],
                    total_population=data['total_population'],
                    population_under_15=data['population_under_15'],
                    population_age_16_24=data['population_16_24'],
                    population_age_25_49=data['population_25_49'],
                    population_age_50_64=data['population_50_64'],
                    population_over_65=data['population_over_65']
                )
                db.session.add(new_record)
                logging.info(f"Added new record for ward {ward_code}")

        # Commit the changes to the database
        db.session.commit()
        logging.info("Population data updated successfully.")

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


def update_occupation_data():
    file_path = 'app/static/json/occupation/occupation.json'  # Path to your JSON file

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        if 'obs' not in data:
            raise ValueError("Invalid data structure in occupation JSON file")

        # Initialize a dictionary to hold data for each ward
        all_data = {}

        # Parse the response to extract relevant information
        for item in data['obs']:
            ward_code = item['geography']['geogcode']
            ward_name = item['geography']['description']
            occupation_category = item['c2021_occ_10']['description']
            value = item['obs_value']['value']

            # Initialize the ward data if not already done
            if ward_code not in all_data:
                all_data[ward_code] = {
                    'ward_name': ward_name,
                    'managers_directors_senior_officials': 0,
                    'professional_occupations': 0,
                    'associate_professional_technical': 0,
                    'administrative_secretarial': 0,
                    'skilled_trades': 0,
                    'caring_leisure_service': 0,
                    'sales_customer_service': 0,
                    'process_plant_machine_operatives': 0,
                    'elementary_occupations': 0
                }

            # Map occupation category to the correct field in the dictionary
            if occupation_category == '1. Managers, directors and senior officials':
                all_data[ward_code]['managers_directors_senior_officials'] = value
            elif occupation_category == '2. Professional occupations':
                all_data[ward_code]['professional_occupations'] = value
            elif occupation_category == '3. Associate professional and technical occupations':
                all_data[ward_code]['associate_professional_technical'] = value
            elif occupation_category == '4. Administrative and secretarial occupations':
                all_data[ward_code]['administrative_secretarial'] = value
            elif occupation_category == '5. Skilled trades occupations':
                all_data[ward_code]['skilled_trades'] = value
            elif occupation_category == '6. Caring, leisure and other service occupations':
                all_data[ward_code]['caring_leisure_service'] = value
            elif occupation_category == '7. Sales and customer service occupations':
                all_data[ward_code]['sales_customer_service'] = value
            elif occupation_category == '8. Process, plant and machine operatives':
                all_data[ward_code]['process_plant_machine_operatives'] = value
            elif occupation_category == '9. Elementary occupations':
                all_data[ward_code]['elementary_occupations'] = value

        # Update or insert the data into the database
        for ward_code, data in all_data.items():
            existing_record = WardOccupation.query.filter_by(ward_code=ward_code).first()
            if existing_record:
                existing_record.managers_directors_senior_officials = data['managers_directors_senior_officials']
                existing_record.professional_occupations = data['professional_occupations']
                existing_record.associate_professional_technical = data['associate_professional_technical']
                existing_record.administrative_secretarial = data['administrative_secretarial']
                existing_record.skilled_trades = data['skilled_trades']
                existing_record.caring_leisure_service = data['caring_leisure_service']
                existing_record.sales_customer_service = data['sales_customer_service']
                existing_record.process_plant_machine_operatives = data['process_plant_machine_operatives']
                existing_record.elementary_occupations = data['elementary_occupations']
                logging.info(f"Updated existing occupation record for ward {ward_code}")
            else:
                new_record = WardOccupation(
                    ward_code=ward_code,
                    ward_name=data['ward_name'],
                    managers_directors_senior_officials=data['managers_directors_senior_officials'],
                    professional_occupations=data['professional_occupations'],
                    associate_professional_technical=data['associate_professional_technical'],
                    administrative_secretarial=data['administrative_secretarial'],
                    skilled_trades=data['skilled_trades'],
                    caring_leisure_service=data['caring_leisure_service'],
                    sales_customer_service=data['sales_customer_service'],
                    process_plant_machine_operatives=data['process_plant_machine_operatives'],
                    elementary_occupations=data['elementary_occupations']
                )
                db.session.add(new_record)
                # logging.info(f"Added new occupation record for ward {ward_code}")

        # Commit the changes to the database
        db.session.commit()
        # logging.info("Occupation data updated successfully.")

    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON in file: {file_path}")
    except ValueError as ve:
        logging.error(ve)
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def update_vehicle_availability_data():
    file_path = 'app/static/json/vehicles/vehicle_availability.json'  # Path to your JSON file

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        if 'obs' not in data:
            raise ValueError("Invalid data structure in vehicle availability JSON file")

        # Initialize a dictionary to hold data for each ward
        all_data = {}

        # Define the mappings for vehicle categories based on the values of c2021_cars_5
        vehicle_categories = {
            1: 'no_cars_vans',                # Value 1 corresponds to No cars or vans in household
            2: 'one_car_van',                 # Value 2 corresponds to One car or van in household
            3: 'two_cars_vans',               # Value 3 corresponds to Two cars or vans in household
            4: 'three_or_more_cars_vans'      # Value 4 corresponds to Three or more cars or vans in household
        }

        # Parse the response to extract relevant information
        for item in data['obs']:
            ward_code = item['geography']['geogcode']
            ward_name = item['geography']['description']

            # Initialize the ward data if not already done
            if ward_code not in all_data:
                all_data[ward_code] = {
                    'ward_name': ward_name,
                    'no_cars_vans': 0,
                    'one_car_van': 0,
                    'two_cars_vans': 0,
                    'three_or_more_cars_vans': 0
                }

            # Get the value of c2021_cars_5
            cars_value = item['c2021_cars_5']['value']
            # Get the corresponding obs_value
            obs_value = item['obs_value']['value']

            # Map the obs_value to the correct category based on the cars_value
            if cars_value in vehicle_categories:
                category_key = vehicle_categories[cars_value]
                all_data[ward_code][category_key] = obs_value

        # Update or insert the data into the database
        for ward_code, data in all_data.items():
            existing_record = WardVehicles.query.filter_by(ward_code=ward_code).first()
            if existing_record:
                existing_record.no_cars_vans = data['no_cars_vans']
                existing_record.one_car_van = data['one_car_van']
                existing_record.two_cars_vans = data['two_cars_vans']
                existing_record.three_or_more_cars_vans = data['three_or_more_cars_vans']
                # logging.info(f"Updated existing vehicle availability record for ward {ward_code}")
            else:
                new_record = WardVehicles(
                    ward_code=ward_code,
                    ward_name=data['ward_name'],
                    no_cars_vans=data['no_cars_vans'],
                    one_car_van=data['one_car_van'],
                    two_cars_vans=data['two_cars_vans'],
                    three_or_more_cars_vans=data['three_or_more_cars_vans']
                )
                db.session.add(new_record)
                # logging.info(f"Added new vehicle availability record for ward {ward_code}")

        # Commit the changes to the database
        db.session.commit()
        # logging.info("Vehicle availability data updated successfully.")

    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON in file: {file_path}")
    except ValueError as ve:
        logging.error(ve)
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


def update_tenure_data():
    file_path = 'app/static/json/tenures/tenures.json'  # Path to your JSON file

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        if 'obs' not in data:
            raise ValueError("Invalid data structure in tenure JSON file")

        # Initialize a dictionary to hold data for each ward
        all_data = {}

        # Define the mappings for tenure categories
        tenure_categories = {
            'Owned: Owns outright': 'owns_outright',
            'Owned: Owns with a mortgage or loan': 'owns_with_mortgage',
            'Shared ownership: Shared ownership': 'shared_ownership',
            'Social rented: Rents from council or Local Authority': 'rents_council',
            'Social rented: Other social rented': 'other_social_rented',
            'Private rented: Private landlord or letting agency': 'rents_private_landlord',
            'Private rented: Other private rented': 'other_private_rented',
            'Lives rent free': 'lives_rent_free'
        }

        # Parse the response to extract relevant information
        for item in data['obs']:
            ward_code = item['geography']['geogcode']
            ward_name = item['geography']['description']
            tenure_category = item['c2021_tenure_9']['description']
            value = item['obs_value']['value']

            # Initialize the ward data if not already done
            if ward_code not in all_data:
                all_data[ward_code] = {
                    'ward_name': ward_name,
                    'owns_outright': 0,
                    'owns_with_mortgage': 0,
                    'shared_ownership': 0,
                    'rents_council': 0,
                    'other_social_rented': 0,
                    'rents_private_landlord': 0,
                    'other_private_rented': 0,
                    'lives_rent_free': 0
                }

            # Map tenure category to the correct field in the dictionary
            if tenure_category in tenure_categories:
                all_data[ward_code][tenure_categories[tenure_category]] = value

        # Update or insert the data into the database
        for ward_code, data in all_data.items():
            existing_record = WardTenures.query.filter_by(ward_code=ward_code).first()
            if existing_record:
                existing_record.owns_outright = data['owns_outright']
                existing_record.owns_with_mortgage = data['owns_with_mortgage']
                existing_record.shared_ownership = data['shared_ownership']
                existing_record.rents_council = data['rents_council']
                existing_record.other_social_rented = data['other_social_rented']
                existing_record.rents_private_landlord = data['rents_private_landlord']
                existing_record.other_private_rented = data['other_private_rented']
                existing_record.lives_rent_free = data['lives_rent_free']
                # logging.info(f"Updated existing tenure record for ward {ward_code}")
            else:
                new_record = WardTenures(
                    ward_code=ward_code,
                    ward_name=data['ward_name'],
                    owns_outright=data['owns_outright'],
                    owns_with_mortgage=data['owns_with_mortgage'],
                    shared_ownership=data['shared_ownership'],
                    rents_council=data['rents_council'],
                    other_social_rented=data['other_social_rented'],
                    rents_private_landlord=data['rents_private_landlord'],
                    other_private_rented=data['other_private_rented'],
                    lives_rent_free=data['lives_rent_free']
                )
                db.session.add(new_record)
                # logging.info(f"Added new tenure record for ward {ward_code}")

        # Commit the changes to the database
        db.session.commit()
        logging.info("Tenure data updated successfully.")

    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON in file: {file_path}")
    except ValueError as ve:
        logging.error(ve)
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


