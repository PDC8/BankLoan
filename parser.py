import os
import openai
import matplotlib
import matplotlib.pyplot as plt
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, render_template, session, redirect, url_for
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader



load_dotenv()
matplotlib.use('Agg')

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
app.secret_key = os.getenv("SESSION_KEY") 

#html of home page
@app.route('/')
def index():
    return render_template('index.html')


#use llama parse to extract info from pdf
def parse_file(file_path):

    parser = LlamaParse(
        result_type="markdown"  # "markdown" and "text" are available
    )

    file_extractor = {".pdf": parser}
    parsed_data = SimpleDirectoryReader(input_files=[file_path], file_extractor=file_extractor).load_data()
    return parsed_data

#function to generate graph
def generate_graphs(data, save_dir='/tmp'):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    plt.figure(figsize=(8, 8))

    #pie chart for discretionary vs. necessary expenses

    labels = 'Discretionary', 'Necessary'
    sizes = [data['discretionary_expense_percentage'], data['necessary_expense_percentage']]
    colors = ['gold', 'blue']
    explode = (0.1, 0)  
    plt.pie(sizes, explode=explode, labels=None, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal') 
    plt.title('Discretionary vs. Necessary Expenses', loc='center')
    plt.legend(labels, loc="lower right")
    pie_path = os.path.join(save_dir, 'discretionary_vs_necessary.png')
    plt.savefig(pie_path)

    #pie chart for debt-to-income ratio
    plt.figure(figsize=(8, 8))

    labels = ['Recurring Income', 'One-Time Income', 'Recurring Expenses', 'One-Time Expenses']
    sizes = [
        data['recurring_income'],
        data['one_time_income'],
        data['recurring_expenses'],
        data['one_time_expenses']
    ]
    colors = ['green', 'lightgreen', 'red', 'pink']
    explode = (0.1, 0.1, 0.1, 0.1)

    plt.pie(sizes, labels=None, colors=colors, explode=explode,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')
    plt.title('Debt-to-Income Ratio (Recurring vs One-Time)', loc='center')
    plt.legend(labels, loc="lower right")
    ratio_path = os.path.join(save_dir, 'debt_to_income_ratio.png')
    plt.savefig(ratio_path)

    #savings vs. cash flow chart
    plt.figure(figsize=(8, 8))
    labels = ['Savings', 'Cash Flow']
    amounts = [data['savings'], data['cash_flow']]
    colors = ['lightgreen', 'red' if data['cash_flow'] < 0 else 'green']
    bars = plt.bar(labels, amounts, color=colors)
    plt.xlabel('Type')
    plt.ylabel('Amount ($)')
    plt.title('Savings vs. Cash Flow', loc='center')
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, height / 2, f"${round(height, 2):.2f}", ha='center', va='center', color='white', fontweight='bold')

    flow_path = os.path.join(save_dir, 'savings_vs_cashflow.png')
    plt.savefig(flow_path)

    plt.close('all')

    return {
        'pie_chart': pie_path,
        'debt_to_income_ratio_chart': ratio_path,
        'savings_vs_cashflow_chart': flow_path
    }


#upload the file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    #save file
    file_path = f'/tmp/{file.filename}'
    file.save(file_path)

    #parse file
    parsed_data = parse_file(file_path)
    
    #use OpenAI to interpret the parsed data
    #fit it to a prompt and format
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "user",
            "content": (
                        f"From the parsed document {parsed_data}, return the following financial information as numbers Show the detailed calculations for each item:"
                        """
                        1. Recurring Income
                        2. One Time Income
                        3. Recurring Expenses
                        4. One Time Expenses
                        5. Percentage of Expenses That Are Discretionary 
                        6. Percentage of Expenses That Are Necessary
                        7. Savings: State the regularity and amount of savings.
                        8. Debt-to-Income Ratio: Calculate the debt-to-income ratio from available data.
                        9. Cash Flow: Calculate the monthly cash flow based on income and expenses.
                        10. Financial Health Indicators: Point out any positive or negative financial habits.

                        Please return the results in a clear and structured format (as numbers) along with the details of your calculations.
                        """
                    ),

            }
        ],
        functions=[
            {
                "name": "return_financial_info",
                "description": "Return financial information in a structured JSON format.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recurring_income": {"type": "number"},
                        "one_time_income": {"type": "number"},
                        "recurring_expenses": {"type": "number"},
                        "one_time_expenses": {"type": "number"},
                        "discretionary_expense_percentage": {"type": "number"},
                        "necessary_expense_percentage": {"type": "number"},
                        "savings": {"type": "number"},
                        "debt_to_income_ratio": {"type": "number"},
                        "cash_flow": {"type": "number"},
                        "financial_health_indicators": {"type": "string"}
                    },
                    "required": [
                        "recurring_income", "one_time_income", "recurring_expenses", 
                        "one_time_expenses", "discretionary_expense_percentage", "necessary_expense_percentage", "savings", 
                        "debt_to_income_ratio", "cash_flow", "financial_health_indicators"
                    ]
                },
            }
        ],
        function_call={
            "name": "return_financial_info"
        }, 
    )

    if response.choices:
        # interpretation = response.choices[0].message.content
        # print(interpretation) 

        financial_data = response.choices[0].message.function_call.arguments
        # print(financial_data)
        data = json.loads(financial_data)
        graphs = generate_graphs(data)

        session['graphs'] = graphs
        return redirect(url_for('show_graphs'))

    else:
        return jsonify({'error': 'Failed to interpret document'}), 500
    
    # graphs = generate_graphs(data1)
    # return jsonify(graphs)

#displays the graphs
@app.route('/graph')
def show_graphs():
    graphs = session.get('graphs')
    if not graphs:
        return "No graphs to display", 400
    return render_template('graph.html', graphs=graphs)

#handle images from /tmp since normally from static folder
@app.route('/tmp/<filename>')
def tmp_file(filename):
    return send_from_directory('/tmp', filename)

if __name__ == '__main__':
    app.run(debug=True)