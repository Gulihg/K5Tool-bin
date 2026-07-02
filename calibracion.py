import struct
import json
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
# BLOQUE 2: RF TABLES (0xC0-0x13F)
# =========================

def parse_rf_tables(data):
    base = 0xC0
    tables = []

    for i in range(0, 0x80, 0x10):  # 8 bloques
        block = list(data[base + i: base + i + 0x10])
        tables.append(block)

    return tables


# =========================
# BLOQUE 3: LUT / THRESHOLDS (0x140-0x1FF)
# =========================

def parse_luts(data):
    base = 0x140

    # uint8 section
    header = list(data[base:base + 8])

    # uint16 section
    lut16 = []
    i = base + 8

    while i + 1 < len(data) and i < 0x200:
        lut16.append(struct.unpack("<H", data[i:i + 2])[0])
        i += 2

    return {
        "header": header,
        "lut16": lut16
    }


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

def dump_block(data, start, end, title):
    print(f"\n=== {title} ({start:04X}-{end-1:04X}) ===")

    for addr in range(start, end, 16):
        row = data[addr:addr+16]
        hexs = " ".join(f"{b:02X}" for b in row)
        ascii = "".join(chr(b) if 32 <= b < 127 else "." for b in row)
        print(f"{addr:04X}: {hexs:<47} | {ascii}")

# =========================
# FULL PARSER
# =========================

def parse_file(path):
    with open(path, "rb") as f:
        data = f.read()

    return {
        "raw": data,
        "sql": parse_sql_table(data),
        "rf": parse_rf_tables(data),
        "luts": parse_luts(data),
    }


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    d = parse_file("k5.bin")

    print_sql(d["sql"])
    export_sql_csv(d["sql"])

    dump_block(d["raw"], 0xC0, 0x140, "RF TABLES")
    dump_block(d["raw"], 0x140, 0x200, "LUT / UNKNOWN")