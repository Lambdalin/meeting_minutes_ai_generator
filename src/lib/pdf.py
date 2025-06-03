from fpdf import FPDF, XPos, YPos


def dataframe_to_table(df):
    headers = tuple(df.columns)
    data = [tuple(row) for row in df.itertuples(index=False, name=None)]
    data = (headers,) + tuple(data)
    return data

def generate_and_save(fecha, hora_inicio, hora_final, lugar, tipo_sesion, asistencia, orden, temas, propuestas, acuerdos, filepath):
    ASISTENCIA = dataframe_to_table(asistencia)
    ORDEN = dataframe_to_table(orden)
    TEMAS = dataframe_to_table(temas)
    PROPUESTAS = dataframe_to_table(propuestas)
    ACUERDOS = dataframe_to_table(acuerdos)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(10, 10, "Acta de reunion",center=True, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(150, 10, f'Lugar: {lugar}')
    pdf.cell(40, 10, f'Fecha: {fecha}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(150, 10, f'Tipo de Sesion: {tipo_sesion}')
    pdf.cell(40, 10, f'Hora: {hora_inicio} - {hora_final}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)


    #Asistencia
    pdf.cell(150, 10, '** Asistencia **', new_x=XPos.LMARGIN, new_y=YPos.NEXT, border="B", markdown=True)
    with pdf.table(borders_layout="NONE", first_row_as_headings=True) as table:
        for data_row in ASISTENCIA:
            row = table.row()
            for datum in data_row:
                row.cell(datum)

    pdf.cell(40, 5, '', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    #Orden del Dia
    with pdf.table(borders_layout="SINGLE_TOP_LINE") as table1:
        for data_row in ORDEN:
            row = table1.row()
            for datum in data_row:
                row.cell(datum)

    pdf.cell(40, 5, '', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    #Temas Desarrollados
    with pdf.table(borders_layout="SINGLE_TOP_LINE") as table2:
        for data_row in TEMAS:
            row = table2.row()
            for datum in data_row:
                row.cell(datum) 

    pdf.cell(150, 20, '** Propuestas **', new_x=XPos.LMARGIN, new_y=YPos.NEXT, border="B", markdown=True)
    #Propuestas Planteadas
    with pdf.table(padding=2, borders_layout="INTERNAL") as table3:
        for data_row in PROPUESTAS:
            row = table3.row()
            for datum in data_row:
                row.cell(datum)

    pdf.cell(150, 20, '** Acuerdos **', new_x=XPos.LMARGIN, new_y=YPos.NEXT, border="B", markdown=True)
    #Acuerdos aprobados
    with pdf.table(padding=2, repeat_headings=0, borders_layout="INTERNAL") as table4:
        for data_row in ACUERDOS:
            row = table4.row()
            for datum in data_row:
                row.cell(datum)
    
    pdf.output(filepath)
