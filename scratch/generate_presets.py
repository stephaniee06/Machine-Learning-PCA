import os
import csv
import random
import math

# Target directory
output_dir = r"d:\pca\Machine-Learning-PCA\Prototype\frontend\public\presets"
os.makedirs(output_dir, exist_ok=True)

# 1. Simple 3D Clusters (normal with a few outliers)
# Features: x, y, z, is_anomaly
def gen_clusters():
    filepath = os.path.join(output_dir, "synthetic_clusters.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y", "z", "is_anomaly"])
        # Normal cluster centered at (0.5, -0.2, 0.1)
        for _ in range(180):
            x = random.gauss(0.5, 0.4)
            y = random.gauss(-0.2, 0.3)
            z = random.gauss(0.1, 0.4)
            writer.writerow([f"{x:.4f}", f"{y:.4f}", f"{z:.4f}", 0])
        # Anomaly outliers far away
        anomalies = [
            (3.5, 3.2, 4.0),
            (-3.0, 2.5, -3.5),
            (2.8, -4.0, 3.0),
            (-2.5, -3.0, -4.2),
            (4.0, -3.5, -3.0),
            (-3.5, 4.0, 3.5),
            (0.5, 4.5, -0.2),
            (4.2, 0.1, 4.0),
            (-4.0, -0.2, 3.0),
            (1.0, -4.5, -3.5)
        ]
        for x, y, z in anomalies:
            writer.writerow([f"{x:.4f}", f"{y:.4f}", f"{z:.4f}", 1])
        # A few random anomalies
        for _ in range(10):
            # Out of normal bounds
            r = random.uniform(3.0, 5.0)
            theta = random.uniform(0, 2*math.pi)
            phi = random.uniform(0, math.pi)
            x = r * math.sin(phi) * math.cos(theta)
            y = r * math.sin(phi) * math.sin(theta)
            z = r * math.cos(phi)
            writer.writerow([f"{x:.4f}", f"{y:.4f}", f"{z:.4f}", 1])

# 2. Cardiovascular Anomaly
# Features: heart_rate, systolic_bp, diastolic_bp, temperature, oxygen_saturation, label
def gen_cardio():
    filepath = os.path.join(output_dir, "cardio_metrics.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["heart_rate", "systolic_bp", "diastolic_bp", "temperature", "oxygen_saturation", "label"])
        # Normal patient stats
        for _ in range(185):
            hr = random.uniform(60, 95)
            sys = random.uniform(110, 128)
            dia = random.uniform(70, 84)
            temp = random.uniform(36.2, 37.3)
            o2 = random.uniform(96, 100)
            writer.writerow([f"{hr:.1f}", f"{sys:.1f}", f"{dia:.1f}", f"{temp:.2f}", f"{o2:.1f}", 0])
        # Anomaly (Critically ill / Spikes)
        for _ in range(15):
            type_anom = random.choice(["tachycardia_hypoxia", "hypertensive_crisis", "fever"])
            if type_anom == "tachycardia_hypoxia":
                hr = random.uniform(130, 160)
                sys = random.uniform(90, 110)
                dia = random.uniform(55, 70)
                temp = random.uniform(36.5, 37.8)
                o2 = random.uniform(85, 91)
            elif type_anom == "hypertensive_crisis":
                hr = random.uniform(90, 110)
                sys = random.uniform(175, 200)
                dia = random.uniform(105, 120)
                temp = random.uniform(36.2, 37.0)
                o2 = random.uniform(94, 98)
            else: # fever
                hr = random.uniform(100, 120)
                sys = random.uniform(115, 130)
                dia = random.uniform(75, 85)
                temp = random.choice([random.uniform(39.2, 40.5), random.uniform(34.0, 35.2)])
                o2 = random.uniform(93, 97)
            writer.writerow([f"{hr:.1f}", f"{sys:.1f}", f"{dia:.1f}", f"{temp:.2f}", f"{o2:.1f}", 1])

# 3. IT Server Performance
# Features: cpu_usage_pct, memory_usage_pct, network_in_mbps, network_out_mbps, disk_io_iops, status
def gen_server():
    filepath = os.path.join(output_dir, "server_metrics.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["cpu_usage_pct", "memory_usage_pct", "network_in_mbps", "network_out_mbps", "disk_io_iops", "status"])
        # Normal server stats
        for _ in range(280):
            cpu = random.uniform(5, 55)
            mem = random.uniform(30, 65)
            net_in = random.uniform(1, 40)
            net_out = random.uniform(1, 60)
            disk = random.uniform(50, 400)
            writer.writerow([f"{cpu:.1f}", f"{mem:.1f}", f"{net_in:.2f}", f"{net_out:.2f}", f"{disk:.1f}", 0])
        # Anomaly (leak, DDOS, freeze)
        for _ in range(20):
            type_anom = random.choice(["ddos", "memory_leak", "disk_saturation", "frozen"])
            if type_anom == "ddos":
                cpu = random.uniform(85, 98)
                mem = random.uniform(50, 75)
                net_in = random.uniform(400, 950) # massive spike
                net_out = random.uniform(10, 50)
                disk = random.uniform(100, 500)
            elif type_anom == "memory_leak":
                cpu = random.uniform(20, 50)
                mem = random.uniform(94, 99.8) # extreme memory
                net_in = random.uniform(1, 20)
                net_out = random.uniform(1, 20)
                disk = random.uniform(5, 50)
            elif type_anom == "disk_saturation":
                cpu = random.uniform(70, 95)
                mem = random.uniform(60, 85)
                net_in = random.uniform(10, 80)
                net_out = random.uniform(10, 80)
                disk = random.uniform(4500, 7000) # massive IOPS
            else: # frozen
                cpu = random.uniform(0, 2)
                mem = random.uniform(80, 90)
                net_in = random.uniform(0.01, 0.1)
                net_out = random.uniform(0.01, 0.1)
                disk = random.uniform(0, 2)
            writer.writerow([f"{cpu:.1f}", f"{mem:.1f}", f"{net_in:.2f}", f"{net_out:.2f}", f"{disk:.1f}", 1])

# 4. Financial Transactions
# Features: amount_usd, tx_speed_kmh, distance_from_home_km, time_of_day_hours, is_fraud
def gen_financial():
    filepath = os.path.join(output_dir, "financial_tx.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["amount_usd", "tx_speed_kmh", "distance_from_home_km", "time_of_day_hours", "is_fraud"])
        # Normal transactions
        for _ in range(235):
            amount = random.expovariate(1 / 40.0) + 1.0 # mostly small
            amount = min(amount, 800.0) # clip
            speed = random.uniform(0, 45) # driving speed or stationary
            dist = random.expovariate(1.0 / 8.0) # mostly close to home
            time = random.uniform(0, 24)
            writer.writerow([f"{amount:.2f}", f"{speed:.1f}", f"{dist:.2f}", f"{time:.2f}", 0])
        # Fraudulent transactions
        for _ in range(15):
            type_anom = random.choice(["impossible_travel", "huge_amount", "speed_spike"])
            if type_anom == "impossible_travel":
                amount = random.uniform(10, 300)
                speed = random.uniform(700, 1100) # plane speed
                dist = random.uniform(800, 9000)
                time = random.uniform(0, 24)
            elif type_anom == "huge_amount":
                amount = random.uniform(4000, 10000) # outlier amount
                speed = random.uniform(0, 30)
                dist = random.uniform(1, 50)
                time = random.uniform(1, 5) # middle of night
            else: # speed spike
                amount = random.uniform(150, 900)
                speed = random.uniform(150, 400)
                dist = random.uniform(100, 600)
                time = random.uniform(0, 24)
            writer.writerow([f"{amount:.2f}", f"{speed:.1f}", f"{dist:.2f}", f"{time:.2f}", 1])

# 5. Industrial Machine Health
# Features: vibration_amplitude_g, bearing_temperature_c, oil_pressure_bar, motor_speed_rpm, anomaly
def gen_industrial():
    filepath = os.path.join(output_dir, "industrial_sensors.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["vibration_amplitude_g", "bearing_temperature_c", "oil_pressure_bar", "motor_speed_rpm", "anomaly"])
        # Normal machinery state
        for _ in range(235):
            vib = random.uniform(0.08, 0.45)
            temp = random.uniform(38.0, 64.0)
            press = random.uniform(3.2, 4.8)
            rpm = random.uniform(1420, 1495)
            writer.writerow([f"{vib:.3f}", f"{temp:.1f}", f"{press:.2f}", f"{rpm:.1f}", 0])
        # Anomaly states
        for _ in range(15):
            type_anom = random.choice(["bearing_failure", "oil_leak", "jammed"])
            if type_anom == "bearing_failure":
                vib = random.uniform(1.8, 4.2) # huge vibration
                temp = random.uniform(85.0, 115.0) # hot bearing
                press = random.uniform(3.0, 4.5)
                rpm = random.uniform(1380, 1460)
            elif type_anom == "oil_leak":
                vib = random.uniform(0.3, 0.8)
                temp = random.uniform(70.0, 90.0)
                press = random.uniform(0.8, 1.8) # pressure drop
                rpm = random.uniform(1400, 1480)
            else: # jammed
                vib = random.uniform(0.8, 1.5)
                temp = random.uniform(90.0, 110.0)
                press = random.uniform(4.0, 5.5)
                rpm = random.uniform(600, 1050)
            writer.writerow([f"{vib:.3f}", f"{temp:.1f}", f"{press:.2f}", f"{rpm:.1f}", 1])

if __name__ == "__main__":
    gen_clusters()
    gen_cardio()
    gen_server()
    gen_financial()
    gen_industrial()
    print("Presets generated successfully!")
