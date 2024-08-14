import PyPDF2
import pandas as pd

#PDF TO CSV 

def extract_text_from_pdf(pdf_path):
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

def process_text(text):
    lines = text.split('\n')

    data = []
    for line in lines:
        data.append(line.split())
    
    return data

def save_to_csv(data, csv_path):
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)

def main(pdf_path, csv_path):
    text = extract_text_from_pdf(pdf_path)
    data = process_text(text)
    save_to_csv(data, csv_path)

pdf_path = 'guide_capa2023.pdf'
csv_path = 'ouput.csv'
main(pdf_path, csv_path)

#Functions :
def normalize_string(s):
   
    return s.lower().strip()
df = pd.read_csv('modifiedoutput.csv')
df['Institution'] = df['Institution'].fillna(method='ffill')
ranking_df = pd.read_csv('matched_institution_rankings.csv')
df1 = pd.read_csv('modifiedoutput.csv')

df.dropna(how='all', inplace=True)

print(df.head())

# Function to list specialities for each institution
def specialities_per_institution(df):
    result = df.groupby('Institution')['Filière'].apply(list).to_dict()
    return result


def total_capacities(df):
    return df.groupby('Institution')['Total général'].sum().to_dict()

def all_specialities(df):
    return df['Filière'].unique().tolist()


def institutions_for_speciality(df, speciality):
    return df[df['Filière'] == speciality]['Institution'].unique().tolist()

def capacity_per_speciality(df):
    return df.groupby('Filière')['Total général'].sum().to_dict()


def capacity_per_institution(df):
    return df.groupby('Institution')['Total général'].sum().to_dict()
def get_most_competitive_institutions():

    informatique_df = df[df['Filière'].str.contains('Informatique', case=False, na=False)]
    
    most_competitive_institutions = informatique_df.sort_values(by='Total général', ascending=False)
    
    return most_competitive_institutions[['Institution', 'Filière', 'Total général']]
def check_university_ranking(institution_name):
     df1 = pd.read_csv('matched_institution_rankings.csv')
     df1['Normalized_Institution'] = df1['Institution'].apply(normalize_string)
     normalized_institution_name = normalize_string(institution_name)
    
    # Check if the normalized institution name is in the DataFrame
     if normalized_institution_name in df1['Normalized_Institution'].values:
        # Get the ranking
        ranking = df1.loc[df1['Normalized_Institution'] == normalized_institution_name, 'Ranking'].values[0]
        return f"L'institution '{institution_name}' est dans le classement des 100 meilleures universités de Tunisie selon le classement Webometrics de juillet 2024 avec un rang de {ranking}."
     
# Example of Usage: 
result = get_most_competitive_institutions()
def generate_questions_and_responses(df):
    questions_responses = []
    
    # Question about most competitive institutions
    question = '<s>[INST]Quelles sont les institutions les plus compétitives ?[/INST]'
    response = "Les institutions les plus compétitives en informatique sont:\n"
    
    for index, row in df.iterrows():
        institution = row['Institution']
        filiere = row['Filière']
        total_general = row['Total général']
        response += f"- {institution}, compétitive car elle offre des spécialités en {filiere} avec un total général de {total_general}.\n"
    
    questions_responses.append(question + response.strip() + '</s>')
    
    return questions_responses
questions_responses = generate_questions_and_responses(result)

# Write to a file:
with open('questions_responses.txt', 'w', encoding='utf-8') as file:
    for item in questions_responses:
        file.write(item + '\n')