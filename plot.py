#!/usr/bin/env python3

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


WHEEL_JOINTS = [
    "w1_link_joint",
    "w2_link_joint",
    "w3_link_joint",
    "w4_link_joint",
    "w5_link_joint",
    "w6_link_joint",
]

PICK_PLACE_JOINTS = [
    "brazo1_link_joint",
    "brazo2_link_joint",
    "paloquebaja_link_joint",
    "pinza_base_link_joint",
    "pinza_d_link_joint",
    "pinza_i_link_joint",
]


def read_rows(path):
    if not path.exists():
        print(f"No existe {path}, se omite.")
        return []

    with path.open(newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def save_plot(output_path, title, xlabel, ylabel):
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)

    handles, labels = plt.gca().get_legend_handles_labels()
    if labels:
        plt.legend()

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Guardado {output_path}")


def plot_acceleration(input_dir, output_dir):
    rows = read_rows(input_dir / "imu.csv")
    if not rows:
        return

    times = [as_float(r.get("time")) for r in rows]
    ax = [as_float(r.get("linear_acceleration_x")) for r in rows]
    ay = [as_float(r.get("linear_acceleration_y")) for r in rows]
    az = [as_float(r.get("linear_acceleration_z")) for r in rows]

    plt.figure()
    plt.plot(times, ax, label="ax")
    plt.plot(times, ay, label="ay")
    plt.plot(times, az, label="az")

    save_plot(
        output_dir / "aceleracion_imu.png",
        "Aceleración vs tiempo",
        "tiempo (s)",
        "aceleración (m/s²)",
    )


def plot_wheel_positions(input_dir, output_dir):
    rows = read_rows(input_dir / "joint_states.csv")
    if not rows:
        return

    wheels = defaultdict(lambda: {"time": [], "position": []})

    for row in rows:
        name = row.get("name")
        if name not in WHEEL_JOINTS:
            continue

        time = as_float(row.get("time"))
        position = as_float(row.get("position"))

        if time is None or position is None:
            continue

        wheels[name]["time"].append(time)
        wheels[name]["position"].append(position)

    if not wheels:
        print("No se encontraron joints de ruedas. Revisa el formato de joint_states.csv.")
        return

    plt.figure()
    for name, values in sorted(wheels.items()):
        plt.plot(values["time"], values["position"], label=name)

    save_plot(
        output_dir / "posicion_ruedas.png",
        "Posición de ruedas vs tiempo",
        "tiempo (s)",
        "posición rueda (rad)",
    )


def plot_gasto(input_dir, output_dir):
    rows = read_rows(input_dir / "joint_states.csv")
    if not rows:
        return

    gasto_por_tiempo = defaultdict(float)
    esfuerzos_encontrados = defaultdict(list)

    for row in rows:
        name = row.get("name")
        if name not in PICK_PLACE_JOINTS:
            continue

        time = as_float(row.get("time"))
        effort = as_float(row.get("effort"))

        if time is None or effort is None:
            continue

        gasto_por_tiempo[time] += abs(effort)
        esfuerzos_encontrados[name].append(effort)

    print("\nResumen de esfuerzos:")
    for joint in PICK_PLACE_JOINTS:
        vals = esfuerzos_encontrados[joint]
        if vals:
            print(
                f"{joint}: min={min(vals):.5f}, max={max(vals):.5f}, "
                f"media={sum(vals) / len(vals):.5f}, muestras={len(vals)}"
            )
        else:
            print(f"{joint}: SIN DATOS")

    if not gasto_por_tiempo:
        print("No se encontraron esfuerzos para calcular el gasto.")
        return

    times = sorted(gasto_por_tiempo.keys())
    gasto = [gasto_por_tiempo[t] for t in times]

    plt.figure()
    plt.plot(times, gasto, label="G_parcial")

    save_plot(
        output_dir / "gasto.png",
        "Gasto parcial vs tiempo",
        "tiempo (s)",
        "G_parcial = suma |effort|",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Genera gráficas PNG desde los CSV del rosbag."
    )
    parser.add_argument(
        "input_dir",
        nargs="?",
        default=".",
        help="Directorio donde están imu.csv y joint_states.csv.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=None,
        help="Directorio donde guardar las imágenes. Por defecto: <input_dir>/output.",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else input_dir / "output"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_wheel_positions(input_dir, output_dir)
    plot_acceleration(input_dir, output_dir)
    plot_gasto(input_dir, output_dir)


if __name__ == "__main__":
    main()
