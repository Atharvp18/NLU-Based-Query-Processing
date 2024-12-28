from flask import Flask, request
import requests
import re
from datetime import datetime

app = Flask(__name__)

@app.route('/api/query', methods=['POST'])
def result():
    wit_api_url = "https://api.wit.ai/message?v=1063283911477629&q=hello"
    server_token = <wit-ai-api-key>

    # Define your Cypher query templates based on recognized intents
    QUERY_TEMPLATES = {
        "retrieve_case01": "MATCH (c:Case) WHERE {match_clause} RETURN c.Case_Name AS Case_Name;",
        "retrieve_precedent02": "MATCH (c:Case) WHERE {match_clause} RETURN c.Precedent AS Precedent;",
        "retrieve_statute03": "MATCH (c:Case) WHERE {match_clause} RETURN c.Statute;",
        "retrieve_date04": "MATCH (c:Case) WHERE {match_clause} RETURN c.Judgement_Date AS Judgement_Date;",
        "retrieve_author05": "MATCH (c:Case) WHERE {match_clause} RETURN c.Author AS Author;",
        "retrieve_bench06": "MATCH (c:Case) WHERE {match_clause} RETURN c.Bench AS Bench;",
        "retrieve_type07": "MATCH (c:Case) WHERE {match_clause} RETURN c.Case_Type AS Case_Type;",
        "retrieve_verdict08": "MATCH (c:Case) WHERE {match_clause} RETURN c.Verdict AS Verdict;",
        "summarize_case09": "MATCH (c:Case) WHERE {match_clause} RETURN c.Summary AS Summary;",
        "retrieve_alldeets10": "MATCH (c:Case) WHERE {match_clause} RETURN c.Case_Name as Case_Name, c.IPC as IPC, c.CRPC as CRPC, c.CPC as CPC, c.Acts as Acts, c.CaseID_CitationID as CaseID_CitationID ,c.Judgement_Date as Judgement_Date, c.Author as Author, c.Bench as Bench, c.Verdict as Verdict;"
    }
        
        # RETURN c.Case_Name, c.IPC, c.CRPC, c.CPC, c.Judgement_Date, c.Author, c.Bench, c.Verdict, c.Location;
    # Function to send a query to Wit.ai and extract intent and entities
    def get_witai_intent_and_entities(query):
        headers = {
            "Authorization": f"Bearer {server_token}"
        }

        params = {
            "q": query
        }

        response = requests.get(wit_api_url, headers=headers, params=params)
        data = response.json()
        intent = data['intents'][0]['name'] if data['intents'] else None
        entities = data['entities']

        return intent, entities

    # Function to generate a Cypher query based on intent and entities
    def generate_cypher_query(intent, entities):
        if intent in QUERY_TEMPLATES:
            query_template = QUERY_TEMPLATES[intent]

            # Generate the MATCH clause based on entities
            match_clause = ""
            for entity_name, entity_values in entities.items():
                # Assuming that each entity has only one value for simplicity
                entity_value = entity_values[0]['body']
                entity_name = entity_name.split(':')[0]

                if entity_name == 'wit$datetime' and 'on' in entity_value.lower():
                # Remove the word 'on' from the datetime value
                    entity_name = 'Judgement_Date'
                    entity_value = entity_value.replace('on', '').strip()

                if entity_name == 'Statute':

                    if 'IPC' in entity_value:
                        key, value = 'IPC', entity_value.split('IPC')[1].strip()
                        section_value = ''.join(filter(str.isdigit, entity_value))
                    elif 'CRPC' in entity_value:
                        key, value = 'CRPC', entity_value.split('CRPC')[1].strip()
                        section_value = ''.join(filter(str.isdigit, entity_value))
                    elif 'CPC' in entity_value:
                        key, value = 'CPC', entity_value.split('CPC')[1].strip()
                        section_value = ''.join(filter(str.isdigit, entity_value))
                    else:
                        key, value = 'Acts', None
                        section_value = ''.join(entity_value)

                    # Use the extracted Section value in the MATCH clause
                    match_clause += f" "
                    #{{{key}: '{section_value}'}})-"
                else:
                    match_clause += f" c.{entity_name}= '{entity_value}' and"

            # Remove the trailing "-"
            match_clause = match_clause.rstrip('and')

            # Replace placeholders with the generated MATCH clause
            cypher_query = query_template.format(match_clause=match_clause)
            if intent == 'retrieve_statute03':
                cypher_query = cypher_query.replace('c.Statute', f'c.IPC as IPC, c.CPC as CPC, c.CRPC as CRPC, c.Acts as Acts')

            # Add WHERE ANY clause for IPC, CPC, and CRPC after the MATCH clause
            if 'Statute' in entity_name:
                where_clauseIPC = f" ANY(ipc IN c.IPC WHERE ipc ='{section_value}')"
                where_clauseCPC = f" ANY(cpc IN c.CPC WHERE cpc ='{section_value}')"
                where_clauseCRPC = f" ANY(crpc IN c.CRPC WHERE crpc ='{section_value}')"
                where_clauseAct = f" ANY(act IN c.Acts WHERE act ='{section_value}')"
                if 'IPC' in entity_value and 'CRPC' not in entity_value and 'CPC' not in entity_value:
                    cypher_query = cypher_query.replace('RETURN', f'{where_clauseIPC}\nRETURN', 1)
                elif 'CPC' in entity_value and 'CRPC' not in entity_value and 'IPC' not in entity_value:
                    cypher_query = cypher_query.replace('RETURN', f'{where_clauseCPC}\nRETURN', 1)
                elif 'CRPC' in entity_value and 'IPC' not in entity_value and 'CPC' not in entity_value:
                    cypher_query = cypher_query.replace('RETURN', f'{where_clauseCRPC}\nRETURN', 1)
                else:
                    cypher_query = cypher_query.replace('RETURN', f'{where_clauseAct}\nRETURN', 1)

            # pattern = r'\bAND\b(?=\s*RETURN\b)'
            # cypher_query = re.sub(pattern, '', cypher_query)
            return cypher_query.strip()
        else:
            return "No intent template found"

    # Example usage:
    data_received = request.json
    user_query = str(data_received['string'])
    witai_intent, witai_entities = get_witai_intent_and_entities(user_query)

    if witai_intent:
        cypher_query = generate_cypher_query(witai_intent, witai_entities)
        if cypher_query:
            # print("Entities:", witai_entities)
            # print("Generated Cypher Query:", cypher_query)
            return {'query': cypher_query}
        else:
            print("No Cypher query template found for the intent.")
    else:
        print("No intent recognized.")