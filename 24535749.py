# Name: Syeda Mehnaz Monsur 
# ID: 24535749

def read_csv(file_name):
    """Loads data from a CSV file into a structured format."""
    records = []
    try:
        with open(file_name, 'r') as file:
            header = file.readline().strip().split(',')
            for line in file:
                entry = line.strip().split(',')
                if len(entry) == len(header) and all(entry):
                    records.append(dict(zip(header, entry)))
    except Exception as e:
        print(f"Failed to read CSV: {e}")
    return records

def read_txt(file_name):
    """Processes data from a TXT file and returns patient admissions."""
    admissions = {}
    try:
        with open(file_name, 'r') as file:
            for line in file:
                fields = line.strip().split(',')
                if len(fields) < 5:
                    continue
                
                # Extracting data
                country = fields[0].split(':')[-1].strip().lower()  # Extract country
                hospital_id = fields[1].split(':')[-1].strip()  # Extract hospital ID
                
                try:
                    covid_cases = int(fields[2].split(':')[-1].strip())  # Extract COVID cases
                    stroke_cases = int(fields[3].split(':')[-1].strip())  # Extract stroke cases
                    cancer_cases = int(fields[4].split(':')[-1].strip())  # Extract cancer cases
                except (ValueError, IndexError) as e:
                    print(f"Error in processing line: {line.strip()}. Details: {e}")
                    continue
                
                # Store admissions data by hospital_id
                if country not in admissions:
                    admissions[country] = {}
                
                admissions[country][hospital_id] = {
                    'covid': covid_cases,
                    'stroke': stroke_cases,
                    'cancer': [cancer_cases]  # Start as a list to append more cases
                }
                
    except Exception as e:
        print(f"Failed to read TXT file: {e}")
    return admissions

def cosine_similarity(deaths, admissions):
    """Calculates cosine similarity between deaths and admissions."""
    if not deaths or not admissions:
        return 0.0
    numerator = sum(d * a for d, a in zip(deaths, admissions))
    sum_deaths_sq = sum(d ** 2 for d in deaths)
    sum_admissions_sq = sum(a ** 2 for a in admissions)
    
    if sum_deaths_sq == 0 or sum_admissions_sq == 0:
        return 0.0
    
    return round(numerator / ((sum_deaths_sq ** 0.5) * (sum_admissions_sq ** 0.5)), 4)

def calculate_variance_highest_two(cancer_cases):
    """Calculates variance for the two highest cancer patient admissions."""
    if len(cancer_cases) < 2:
        return 0.0
    
    # Extract the two highest cancer admission values
    highest_two = sorted(cancer_cases, reverse=True)[:2]
    
    # Calculate the mean of the two highest values
    mean = sum(highest_two) / 2
    
    # Calculate the squared differences and sum them
    squared_diff_sum = sum((x - mean) ** 2 for x in highest_two)
    
    # Divide by N-1 (which is 1, since there are only 2 values)
    variance = squared_diff_sum / (2 - 1)
    
    return round(variance, 4)

def main(CSVfile, TXTfile, category_filter):
    """Main function to process data from CSV and TXT files and calculate required values."""
    
    # Read data from CSV and TXT files
    hospital_data = read_csv(CSVfile)
    admissions_data = read_txt(TXTfile)

    # Prepare OP1 as a list
    OP1 = [{}, {}, {}]  # To hold hospital IDs, deaths, and COVID/stroke sums
    death_count_per_country = {}  # Track deaths per country for averages later

    # Organize country-wise data for all hospitals for OP1 and OP2
    for entry in hospital_data:
        country = entry['country'].lower()
        hospital_id = entry['hospital_ID']
        
        deaths_2022 = int(entry['No_of_deaths_in_2022'])
        deaths_2023 = int(entry['No_of_deaths_in_2023'])

        # Add hospital IDs to OP1[0] for all hospitals
        if country not in OP1[0]:
            OP1[0][country] = []
        OP1[0][country].append(hospital_id)

        # Add deaths to OP1[1] for all hospitals
        if country not in OP1[1]:
            OP1[1][country] = []
        OP1[1][country].append(deaths_2022)  # Use deaths in 2022

        # Track death count for averages later
        if country not in death_count_per_country:
            death_count_per_country[country] = [deaths_2022, deaths_2023]
        else:
            death_count_per_country[country][0] += deaths_2022
            death_count_per_country[country][1] += deaths_2023

        # Initialize COVID + stroke cases in OP1[2] if not already done for that country
        if country not in OP1[2]:
            OP1[2][country] = []

        # If hospital_id matches, append COVID and stroke cases directly to the country's list
        if country in admissions_data and hospital_id in admissions_data[country]:
            covid_cases = admissions_data[country][hospital_id]['covid']
            stroke_cases = admissions_data[country][hospital_id]['stroke']
            total_cases = covid_cases + stroke_cases

            OP1[2][country].append(total_cases)

    # Compute cosine similarity between deaths and COVID/stroke cases for OP2
    OP2 = {}
    for country in admissions_data:
        deaths = OP1[1].get(country, [])
        covid_stroke_cases = OP1[2].get(country, [])
        OP2[country] = cosine_similarity(deaths, covid_stroke_cases)

    # Calculate cancer variance for each country for OP3 (using only the two highest values from hospitals matching the category)
    OP3 = {}
    for country, hospitals in admissions_data.items():
        cancer_cases = []
        for hospital_id, data in hospitals.items():
            # Only consider hospitals of the specified category for OP3
            if hospital_id in [entry['hospital_ID'] for entry in hospital_data if entry['hospital_category'].lower() == category_filter.lower() and entry['country'].lower() == country]:
                cancer_cases.extend(data['cancer'])  # Collect all cancer cases from the hospital

        if cancer_cases:
            variance = calculate_variance_highest_two(cancer_cases)  # Use modified function
            OP3[country] = variance

    # Gather hospital category data for OP4
    OP4 = {}
    for entry in hospital_data:
        hospital_category = entry['hospital_category'].lower()
        country = entry['country'].lower()

        # Only consider hospitals of the specified category for OP4
        if hospital_category == category_filter.lower():  # Changed to equality check
            if hospital_category not in OP4:
                OP4[hospital_category] = {}

            if country not in OP4[hospital_category]:
                OP4[hospital_category][country] = [0, 0, 0.0]  # [avg_females, max_staff, death_change]

            avg_females = float(entry['female_patients'])
            staff_count = int(entry['no_of_staff'])
            deaths_2022 = int(entry['No_of_deaths_in_2022'])
            deaths_2023 = int(entry['No_of_deaths_in_2023'])

            OP4[hospital_category][country][0] += avg_females
            OP4[hospital_category][country][1] = max(OP4[hospital_category][country][1], staff_count)
            OP4[hospital_category][country][2] += deaths_2023 - deaths_2022

    # Calculate final averages and percentage changes for OP4
    for category in OP4:
        for country in OP4[category]:
            stats = OP4[category][country]
            avg_females = stats[0] / len([entry for entry in hospital_data if entry['hospital_category'].lower() == category and entry['country'].lower() == country]) if country in OP4[category] else 0  # Ensure no division by zero

            # Calculate total deaths for 2022 for hospitals of the specified category
            total_deaths_2022 = sum(int(entry['No_of_deaths_in_2022']) for entry in hospital_data if entry['hospital_category'].lower() == category and entry['country'].lower() == country)

            death_change = (stats[2] / total_deaths_2022 * 100) if total_deaths_2022 else 0  # Use total deaths for 2022 from specified category
            OP4[category][country] = [round(avg_females, 4), stats[1], round(death_change, 4)]

    return OP1, OP2, OP3, OP4
    
# Example run:
OP1, OP2, OP3, OP4 = main('hospital_data.csv', 'disease.txt', 'children')

print(len(OP1))
print(OP1[0]['afghanistan'])
print(OP1[1]['afghanistan'])
print(OP1[2]['afghanistan'])
print(len(OP2))
print(OP2['afghanistan'])
print(OP2['albania'])
print(OP3['afghanistan'])
print(OP3['brunei darussalam'])
print(len(OP4['children']))
print(OP4['children']['canada'])

