from flask import Flask, request, jsonify
import pandas as pd
import json
import sqlite3
import datetime

app = Flask(__name__)


@app.route('/snr_report', methods=['POST'])
def processjson():
    data = request.get_json()
    coil_name = data['coil_name']
    seq_id = data['seq_id']
    return jsonify({'result':'success','coil_name':coil_name, 'seq_id':seq_id})


@app.route('/patients', methods=['POST'])
def patients():

    # try:
    data = request.get_json()
    coil_name = data['coil_name']
    seq_id = data['seq_id']
    file_path = 'C:/Users/698023/philips%20MRI%20coil/301951420_{coil_name}_0{seq_id}.htm'.format(coil_name = coil_name, seq_id = seq_id)
    df = pd.read_html(file_path)
    df_final = pd.concat([df[2].T,df[5].T,df[8].T,df[11].T], ignore_index=True)
    df_final.columns = df_final.iloc[0]
    df_final.drop([0,9,18,27],inplace=True)
    df_final.drop(columns = ['Bw/Pixel','Trans_Q','Drive','RF_Factor','Rec_Q','Req_Att','Echo_No','Dyn_Scan_No','Dist_sel',
    'Echo_Time','SNR_Factor','Art_Level','Int_Unif','S/N (C)'], inplace = True)
    df_final.columns = df_final.columns.str.replace('[^A-Za-z0-9]+', '_').str.strip('_')
    patient_list = df_final.to_json(orient='records')

    currentDateTime = datetime.datetime.now()
    conn = sqlite3.connect("patient.db")
    cursor = conn.cursor()
    sql_query = """create table IF NOT EXISTS patients_data ( coil_name text, sequence_id text, created_at TIMESTAMP, file_type text, data json)"""
    cursor.execute(sql_query)
    cursor.execute("insert into patients_data values (?,?,?,?,?)",[coil_name,seq_id,currentDateTime,'STP_FILE', json.dumps(patient_list)])
    conn.commit()
    conn.close()
    
    return patient_list, 200
    # except sqlite3.error as e:
    #     print(e)
    

# if __name__ == '__main__':
#     app.run(debug=True)

