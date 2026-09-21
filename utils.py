from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import cv2

def calculateBMI(data : dict):
    if len(data['userHeight']) and len(data['userWeight']):
        BMI = round(float(data['userWeight'][-1][1])/((float(data['userHeight'][-1][1])/100)**2), 2)
        if BMI >= 27:
            BMI_text = "，BMI過高"
        elif BMI >= 18.5:
            BMI_text = "，BMI適中"
        else:
            BMI_text = "，BMI過低"
        return f"，BMI為{BMI}{BMI_text}。"
    elif len(data['userHeight']):
        return f"，缺少體重資訊因此不能計算BMI值。"
    else:
        return f"，缺少身高資訊因此不能計算BMI值。"

def calculateDayCalories(data : dict):
    now_time = datetime.now().strftime("%m/%d/%Y")
    heats = [float(heat) for time, heat in data['userCalories'] if time.startswith(now_time)]
    return sum(heats)

def plotHealth(data : dict, user_id):
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    folder_path = f'./static/{user_id}/'
    
    data_H = data['userHeight'][-30:] if len(data['userHeight']) > 30 else data['userHeight']
    data_W = data['userWeight'][-30:] if len(data['userWeight']) > 30 else data['userWeight']
    data_BS = data['userBloodSuger'][-30:] if len(data['userBloodSuger']) > 30 else data['userBloodSuger']
    data_BP = data['userBloodPressure'][-30:] if len(data['userBloodPressure']) > 30 else data['userBloodPressure']
    if len(data_H):
        plt.plot([float(H) for time, H in data_H], label = '身高')
    if len(data_W):
        plt.plot([float(W) for time, W in data_W], label = '體重')
    plt.title('近30次身高/體重紀錄')
    plt.tick_params(
        axis='x',       
        which='both',     
        bottom=False,      
        top=False,        
        labelbottom=False
    )
    plt.xlabel('近30次時間軸')
    plt.ylabel('身高/體重')
    plt.legend()
    plt.grid("--", alpha = 0.4)
    plt.savefig(f'{folder_path}height.png')
    plt.close()
    plt.cla()
    plt.clf()

    if len(data_BS):
        plt.plot([float(S) for time, S in data_BS], label = '血糖')
    if len(data_BP):
        plt.plot([float(P.split('/')[0]) for time, P in data_BP], label = '收縮壓')
    if len(data_BP):
        plt.plot([float(P.split('/')[1]) for time, P in data_BP], label = '舒張壓')
    plt.title('近30次血糖/血壓紀錄')
    plt.tick_params(
        axis='x',       
        which='both',     
        bottom=False,      
        top=False,        
        labelbottom=False
    )
    plt.xlabel('近30次時間軸')
    plt.ylabel('血糖/血壓')
    plt.legend()
    plt.grid("--", alpha = 0.4)
    plt.savefig(f'{folder_path}heat.png')
    image_1 = cv2.imread(f'{folder_path}height.png')
    image_2 = cv2.imread(f'{folder_path}heat.png')
    cv2.imwrite(f"{folder_path}output.png", np.hstack((image_1, image_2)))
