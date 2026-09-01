"""
Testes unitários para:

    core/usefuls/pattern.py
    core/usefuls/regex_pattern.py

Objetivo:

    Garantir que os padrões regex utilizados pelo processamento SICRO:

        - reconheçam linhas válidas;
        - rejeitem linhas incompatíveis;
        - extraiam corretamente os grupos nomeados;
        - mantenham o comportamento esperado das variantes ALFA/BETA;
        - direcionem corretamente cada caso através de CompositionRegex.

IMPORTANTE:

    Estes testes não utilizam banco de dados.

Executar:

    python manage.py test core.tests.test_pattern_regex -v 2
"""

import unittest

from core.usefuls.pattern import (
    FIRST_ROW_PATTERN,
    SECOND_ROW_PATTERN,
    THIRD_ROW_PATTERN,
    THIRD_ROW_PATTERN_BETA,
    FOURTH_ROW_PATTERN,

    EQUIPEMENT_PATTERN,
    EQUIPEMENT_PATTERN_ALFA,
    EQUIPEMENT_PATTERN_BETA,

    WORKMANSHIP_PATTERN,

    MATERIAL_PATTERN,
    MATERIAL_PATTERN_ALFA,
    MATERIAL_PATTERN_BETA,

    FIXED_TIME_PATTERN,

    TRANSPORTATION_PATTERN,
    TRANSPORTATION_PATTERN_ALFA,

    ACTIVITIES_PATTERN,
    ACTIVITIES_PATTERN_ALFA,
    ACTIVITIES_PATTERN_BETA,

    BREAK_PATTERN,
    LAST_PATTERN,
    LAST_HEADER_PATTERN,

    GENERAL_INPUT_PATTERN,
    GENERAL_INPUT_PATTERN_ALFA,
    GENERAL_INPUT_PATTERN_BETA,
)

from core.usefuls.regex_pattern import CompositionRegex

from core.usefuls.pattern import (
    FIRST_ROW_REGEX,
    FIC_REGEX,
    DATA_BASE_REGEX,
    COMPOSITION_CODE_REGEX,
    PRODUCTION_REGEX,
    UNIT_REGEX,

    EQUIPEMENT_CODE_REGEX,
    EQUIPEMENT_CODE_REGEX_BETA,
    EQUIPEMENT_QUANT_REGEX,
    EQUIPEMENT_QUANT_REGEX_ALFA,
    EQUIPEMENT_UTIL_REGEX,
    EQUIPEMENT_UTIL_REGEX_ALFA,

    WORKMANSHIP_CODE_REGEX,
    WORKMANSHIP_QUANT_REGEX,

    BREAK_REGEX,
    LAST_REGEX,
    LAST_HEADER_REGEX,

    MATERIAL_CODE_REGEX,
    MATERIAL_QUANT_REGEX,
    MATERIAL_QUANT_REGEX_ALFA,
    MATERIAL_CODE_REGEX_BETA,

    FIXED_UNIT_REGEX,
    FIXED_CODE_REGEX,
    FIXED_MATERIAL_CODE_REGEX,
    FIXED_MATERIAL_QUANT_REGEX,

    ACTIVITIES_CODE_REGEX,
    ACTIVITIES_QUANT_REGEX,
    ACTIVITIES_QUANT_REGEX_ALFA,
    ACTIVITIES_CODE_REGEX_BETA,

    TRANSPORTATION_UNIT_REGEX,
    TRANSPORTATION_PV_CODE_REGEX,
    TRANSPORTATION_LN_CODE_REGEX,
    TRANSPORTATION_RP_CODE_REGEX,
    TRANSPORTATION_MATERIAL_CODE_REGEX,
    TRANSPORTATION_MATERIAL_QUANT_REGEX,

    GENERAL_INPUT_QUANT_REGEX,
    GENERAL_INPUT_CODE_REGEX,
    GENERAL_INPUT_QUANT_REGEX_ALFA,
    GENERAL_INPUT_CODE_REGEX_BETA,
)


# ============================================================================
# COMPOSITION REGEX
# ============================================================================


class CompositionRegexBasicTests(unittest.TestCase):
    """
    Testes básicos da classe CompositionRegex.
    """

    def setUp(self):
        self.regex = CompositionRegex()

    def test_get_regex_returns_named_group(self):
        """
        get_regex() deve retornar o grupo solicitado quando a expressão
        corresponde à linha.
        """

        evaluated = (
            "Janeiro/2023 24,63000 m"
        )

        result = self.regex.get_regex(
            THIRD_ROW_PATTERN,
            evaluated,
            DATA_BASE_REGEX,
        )

        self.assertEqual(
            result,
            "Janeiro/2023",
        )

    def test_get_regex_returns_none_when_pattern_does_not_match(self):
        """
        Quando a linha não corresponde ao padrão, o retorno deve ser None.
        """

        evaluated = "linha completamente inválida"

        result = self.regex.get_regex(
            THIRD_ROW_PATTERN,
            evaluated,
            DATA_BASE_REGEX,
        )

        self.assertIsNone(result)

    def test_switch_regex_composition_code(self):
        """
        COMPOSITION_CODE_REGEX deve utilizar FOURTH_ROW_PATTERN.
        """

        evaluated = "2003979"

        result = self.regex.switch_regex(
            COMPOSITION_CODE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "2003979",
        )

    def test_switch_regex_invalid_case_returns_none(self):
        """
        Um caso desconhecido não deve gerar uma correspondência.
        """

        result = self.regex.switch_regex(
            "CASO_INEXISTENTE",
            "qualquer coisa",
        )

        self.assertIsNone(result)


# ============================================================================
# PRIMEIRAS LINHAS / CABEÇALHO
# ============================================================================


class HeaderPatternTests(unittest.TestCase):

    def test_first_row_pattern(self):
        evaluated = (
            "Valores em reais (R$)"
            "Custo Unitário de Referência"
            "Produção da equipe"
        )

        match = __import__("re").match(
            FIRST_ROW_PATTERN,
            evaluated,
        )

        self.assertIsNotNone(match)

    def test_second_row_extracts_fic(self):
        evaluated = (
            "SISTEMA DE CUSTOS REFERENCIAIS DE OBRAS - SICRO "
            "FIC 0,12345 "
            "CGCIT DNIT"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            FIC_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "0,12345",
        )

    def test_third_row_extracts_database(self):
        evaluated = (
            "Janeiro/2023 24,63000 m"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            DATA_BASE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "Janeiro/2023",
        )

    def test_third_row_extracts_production(self):
        evaluated = (
            "Janeiro/2023 24,63000 m"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            PRODUCTION_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "24,63000",
        )

    def test_third_row_extracts_unit(self):
        evaluated = (
            "Janeiro/2023 24,63000 m"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            UNIT_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "m",
        )

    def test_third_row_beta_extracts_database(self):
        evaluated = (
            "algum texto "
            "Janeiro/2023 "
            "Produçãodaequipe "
            "24,63000 m"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            DATA_BASE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "Janeiro/2023",
        )

    def test_fourth_row_composition_code(self):
        evaluated = "2003979"

        regex = CompositionRegex()

        result = regex.switch_regex(
            COMPOSITION_CODE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "2003979",
        )


# ============================================================================
# EQUIPAMENTOS
# ============================================================================


class EquipmentPatternTests(unittest.TestCase):

    def test_equipment_pattern_extracts_code(self):
        evaluated = (
            "100000,0000 "
            "100000,0000 "
            "100000,0000 "
            "42,19 "
            "1,00 "
            "1,00000 "
            "Extrusora para sarjeta "
            "E9102"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            EQUIPEMENT_CODE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "E9102",
        )

    def test_equipment_pattern_extracts_quantity(self):
        evaluated = (
            "100000,0000 "
            "100000,0000 "
            "100000,0000 "
            "42,19 "
            "1,00 "
            "1,00000 "
            "Extrusora para sarjeta "
            "E9102"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            EQUIPEMENT_QUANT_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "1,00000",
        )

    def test_equipment_pattern_extracts_utilization(self):
        evaluated = (
            "100000,0000 "
            "100000,0000 "
            "100000,0000 "
            "42,19 "
            "1,00 "
            "1,00000 "
            "Extrusora para sarjeta "
            "E9102"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            EQUIPEMENT_UTIL_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "1,00",
        )

    def test_equipment_beta_extracts_code(self):
        evaluated = (
            "Extrusora para sarjeta E9102"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            EQUIPEMENT_CODE_REGEX_BETA,
            evaluated,
        )

        self.assertEqual(
            result,
            "E9102",
        )

    def test_equipment_invalid_code_is_rejected(self):
        evaluated = (
            "100000,0000 "
            "100000,0000 "
            "100000,0000 "
            "42,19 "
            "1,00 "
            "1,00000 "
            "Extrusora "
            "X9102"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            EQUIPEMENT_CODE_REGEX,
            evaluated,
        )

        self.assertIsNone(result)


# ============================================================================
# MÃO DE OBRA
# ============================================================================


class WorkmanPatternTests(unittest.TestCase):

    def test_workmanship_extracts_code(self):
        evaluated = (
            "27,5468 "
            "27,5468 "
            "h "
            "1,00000 "
            "Pedreiro "
            "P9821"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            WORKMANSHIP_CODE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "P9821",
        )

    def test_workmanship_extracts_quantity(self):
        evaluated = (
            "27,5468 "
            "27,5468 "
            "h "
            "1,00000 "
            "Pedreiro "
            "P9821"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            WORKMANSHIP_QUANT_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "1,00000",
        )

    def test_workmanship_accepts_month_unit(self):
        evaluated = (
            "27,5468 "
            "27,5468 "
            "mês "
            "1,00000 "
            "Profissional "
            "P9821"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            WORKMANSHIP_CODE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "P9821",
        )


# ============================================================================
# MATERIAIS
# ============================================================================


class MaterialPatternTests(unittest.TestCase):

    def test_material_pattern_extracts_code(self):
        evaluated = (
            "10,0000 "
            "20,0000 "
            "Cimento "
            "1,25000 "
            "kg "
            "M1001"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            MATERIAL_CODE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "M1001",
        )

    def test_material_pattern_extracts_quantity(self):
        evaluated = (
            "10,0000 "
            "20,0000 "
            "Cimento "
            "1,25000 "
            "kg "
            "M1001"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            MATERIAL_QUANT_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "1,25000",
        )

    def test_material_beta_extracts_code(self):
        evaluated = (
            "Cimento Portland M1001"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            MATERIAL_CODE_REGEX_BETA,
            evaluated,
        )

        self.assertEqual(
            result,
            "M1001",
        )

    def test_material_invalid_code_is_rejected(self):
        evaluated = (
            "10,0000 "
            "20,0000 "
            "Cimento "
            "1,25000 "
            "kg "
            "X1001"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            MATERIAL_CODE_REGEX,
            evaluated,
        )

        self.assertIsNone(result)


# ============================================================================
# TEMPO FIXO
# ============================================================================


class FixedTimePatternTests(unittest.TestCase):

    def test_fixed_time_extracts_unit(self):
        evaluated = (
            "t "
            "0,33360 "
            "59,0400 "
            "59,0400 "
            "5919534 "
            "1107928 "
            "Caminhão betoneira"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            FIXED_UNIT_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "t ",
        )

    def test_fixed_time_extracts_quantity(self):
        evaluated = (
            "t "
            "0,33360 "
            "59,0400 "
            "59,0400 "
            "5919534 "
            "1107928 "
            "Caminhão betoneira"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            FIXED_MATERIAL_QUANT_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "0,33360",
        )

    def test_fixed_time_extracts_code(self):
        evaluated = (
            "t "
            "0,33360 "
            "59,0400 "
            "59,0400 "
            "5919534 "
            "1107928 "
            "Caminhão betoneira"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            FIXED_CODE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "5919534",
        )

    def test_fixed_time_extracts_material_code(self):
        evaluated = (
            "t "
            "0,33360 "
            "59,0400 "
            "59,0400 "
            "5919534 "
            "1107928 "
            "Caminhão betoneira"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            FIXED_MATERIAL_CODE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "1107928",
        )


# ============================================================================
# ATIVIDADES AUXILIARES
# ============================================================================


class ActivitiesPatternTests(unittest.TestCase):

    def test_activity_pattern_extracts_code(self):
        evaluated = (
            "379,4400 "
            "379,4400 "
            "m³ "
            "0,13900 "
            "Concreto fck = 20 MPa "
            "1107928"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            ACTIVITIES_CODE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "1107928",
        )

    def test_activity_pattern_extracts_quantity(self):
        evaluated = (
            "379,4400 "
            "379,4400 "
            "m³ "
            "0,13900 "
            "Concreto fck = 20 MPa "
            "1107928"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            ACTIVITIES_QUANT_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "0,13900",
        )

    def test_activity_beta_extracts_code(self):
        evaluated = (
            "Concreto fck = 20 MPa 1107928"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            ACTIVITIES_CODE_REGEX_BETA,
            evaluated,
        )

        self.assertEqual(
            result,
            "1107928",
        )


# ============================================================================
# TRANSPORTE
# ============================================================================


class TransportationPatternTests(unittest.TestCase):

    def test_transportation_extracts_unit(self):
        evaluated = (
            "Concreto "
            "0,33360 "
            "tkm "
            "5914539 "
            "5914554 "
            "5914569 "
            "1107928"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            TRANSPORTATION_UNIT_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "tkm",
        )

    def test_transportation_extracts_quantity(self):
        evaluated = (
            "Concreto "
            "0,33360 "
            "tkm "
            "5914539 "
            "5914554 "
            "5914569 "
            "1107928"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            TRANSPORTATION_MATERIAL_QUANT_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "0,33360",
        )

    def test_transportation_extracts_ln_code(self):
        evaluated = (
            "Concreto "
            "0,33360 "
            "tkm "
            "5914539 "
            "5914554 "
            "5914569 "
            "1107928"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            TRANSPORTATION_LN_CODE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "5914539",
        )

    def test_transportation_extracts_rp_code(self):
        evaluated = (
            "Concreto "
            "0,33360 "
            "tkm "
            "5914539 "
            "5914554 "
            "5914569 "
            "1107928"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            TRANSPORTATION_RP_CODE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "5914554",
        )

    def test_transportation_extracts_pv_code(self):
        evaluated = (
            "Concreto "
            "0,33360 "
            "tkm "
            "5914539 "
            "5914554 "
            "5914569 "
            "1107928"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            TRANSPORTATION_PV_CODE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "5914569",
        )

    def test_transportation_extracts_material_code(self):
        evaluated = (
            "Concreto "
            "0,33360 "
            "tkm "
            "5914539 "
            "5914554 "
            "5914569 "
            "1107928"
        )

        result = self.regex_result(
            TRANSPORTATION_MATERIAL_CODE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "1107928",
        )

    def regex_result(self, case, evaluated):
        regex = CompositionRegex()

        return regex.switch_regex(
            case,
            evaluated,
        )


# ============================================================================
# MARCADORES DE CONTROLE
# ============================================================================


class ControlPatternTests(unittest.TestCase):

    def setUp(self):
        self.regex = CompositionRegex()

    def test_break_pattern(self):
        evaluated = (
            "Custo horário total de mão de obra 67,2306"
        )

        result = self.regex.switch_regex(
            BREAK_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "Custo horário total de mão de obra",
        )

    def test_last_pattern(self):
        evaluated = "Obs: alguma observação"

        result = self.regex.switch_regex(
            LAST_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "Obs:",
        )

    def test_last_header_pattern(self):
        evaluated = (
            "Quantidade A - EQUIPAMENTOS"
        )

        result = self.regex.switch_regex(
            LAST_HEADER_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "Quantidade A - EQUIPAMENTOS",
        )


# ============================================================================
# GENERAL INPUT
# ============================================================================


class GeneralInputPatternTests(unittest.TestCase):

    def test_general_input_extracts_material_code(self):
        evaluated = (
            "10,0000 "
            "20,0000 "
            "Cimento "
            "1,25000 "
            "kg "
            "M1001"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            GENERAL_INPUT_CODE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "M1001",
        )

    def test_general_input_extracts_workman_code(self):
        evaluated = (
            "10,0000 "
            "20,0000 "
            "Pedreiro "
            "1,00000 "
            "h "
            "P9821"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            GENERAL_INPUT_CODE_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "P9821",
        )

    def test_general_input_extracts_quantity(self):
        evaluated = (
            "10,0000 "
            "20,0000 "
            "Cimento "
            "1,25000 "
            "kg "
            "M1001"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            GENERAL_INPUT_QUANT_REGEX,
            evaluated,
        )

        self.assertEqual(
            result,
            "1,25000",
        )

    def test_general_input_beta_extracts_material_code(self):
        evaluated = (
            "Cimento Portland M1001"
        )

        regex = CompositionRegex()

        result = regex.switch_regex(
            GENERAL_INPUT_CODE_REGEX_BETA,
            evaluated,
        )

        self.assertEqual(
            result,
            "M1001",
        )


# ============================================================================
# TESTES DIRETOS DOS PADRÕES
# ============================================================================


class DirectPatternValidationTests(unittest.TestCase):

    def test_composition_code_requires_seven_digits(self):
        import re

        self.assertIsNotNone(
            re.fullmatch(
                FOURTH_ROW_PATTERN,
                "2003979",
            )
        )

        self.assertIsNone(
            re.fullmatch(
                FOURTH_ROW_PATTERN,
                "200397",
            )
        )

        self.assertIsNone(
            re.fullmatch(
                FOURTH_ROW_PATTERN,
                "20039790",
            )
        )

    def test_equipment_code_requires_e_or_a_prefix(self):
        import re

        self.assertIsNotNone(
            re.search(
                r"[EA]\d{4}$",
                "Equipamento E9102",
            )
        )

        self.assertIsNotNone(
            re.search(
                r"[EA]\d{4}$",
                "Equipamento A9102",
            )
        )

        self.assertIsNone(
            re.search(
                r"[EA]\d{4}$",
                "Equipamento P9102",
            )
        )

    def test_material_code_requires_m_prefix(self):
        import re

        self.assertIsNotNone(
            re.search(
                r"M\d{4}$",
                "Material M1001",
            )
        )

        self.assertIsNone(
            re.search(
                r"M\d{4}$",
                "Material P1001",
            )
        )

    def test_workman_code_requires_p_prefix(self):
        import re

        self.assertIsNotNone(
            re.search(
                r"P\d{4}$",
                "Pedreiro P9821",
            )
        )

        self.assertIsNone(
            re.search(
                r"P\d{4}$",
                "Pedreiro M9821",
            )
        )