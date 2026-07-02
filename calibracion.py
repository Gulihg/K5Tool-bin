import struct
import csv

SQLS = range(10)

PARAMS = [
    "open_rssi",
    "close_rssi",
    "open_noise",
    "close_noise",
    "open_glitch",
    "close_glitch"
]


# =========================
# BLOQUE 1: SQL CALIBRATION
# =========================

def parse_sql_table(data):
    base = 0x00

    result = {
        "band_4_7": {sql: {} for sql in SQLS},
        "band_1_3": {sql: {} for sql in SQLS},
    }

    for band_index, band in enumerate(["band_4_7", "band_1_3"]):
        band_base = base + band_index * 0x60

        for sql in SQLS:
            for i, param in enumerate(PARAMS):
                offset = band_base + i * 0x10 + sql
                result[band][sql][param] = data[offset]

    return result


# =========================
# PRINT SQL
# =========================

def print_sql(sql):
    for band in sql:
        print(f"\n=== {band} ===")

        # Cabecera
        print("Parametro\t" + "\t".join(f"SQL{s}" for s in SQLS))

        # Filas
        for param in PARAMS:
            valores = [str(sql[band][s][param]) for s in SQLS]
            print(f"{param}\t" + "\t".join(valores))


# =========================
# CREA CSV
# =========================


def export_sql_csv(sql, filename="Calibracion.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(
            ["Band", "Parametro"] + [f"SQL{s}" for s in SQLS]
        )

        for band in sql:
            for param in PARAMS:
                fila = [band, param]
                fila.extend(sql[band][s][param] for s in SQLS)
                writer.writerow(fila)


# =========================
# DUMP HEX BLOCK
# =========================
#
#def dump_block(data, start, end, title):
#    print(f"\n=== {title} ({start:04X}-{end-1:04X}) ===")
#
#    for addr in range(start, end, 16):
#        row = data[addr:addr+16]
#        hexs = " ".join(f"{b:02X}" for b in row)
#        ascii = "".join(chr(b) if 32 <= b < 127 else "." for b in row)
#        print(f"{addr:04X}: {hexs:<47} | {ascii}")
#
# =========================
# FULL PARSER
# =========================

def parse_file(path):
    with open(path, "rb") as f:
        data = f.read()

    return {
        "raw": data,
        "sql": parse_sql_table(data),
    }


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    d = parse_file("k5.bin")

    print_sql(d["sql"])
    export_sql_csv(d["sql"])
