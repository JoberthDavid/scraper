# import re

# from core.usefuls.pattern import *


# class CompositionRegex:

#     def get_regex( self, pattern: str, evaluated: str, group: str ) -> str|None:
#         if ( re.match( pattern, evaluated ) is not None ):
#             chosen_regex = re.match( pattern, evaluated ).group( group )
#         else:
#             chosen_regex = None
#         return chosen_regex

#     def switch_regex(self, case: str, evaluated: str ) -> str:
#         if case == FIC_REGEX:
#             return self.get_regex( SECOND_ROW_PATTERN, evaluated, case )
#         elif case == DATA_BASE_REGEX or case == PRODUCTION_REGEX or case == UNIT_REGEX:
#             if self.get_regex( THIRD_ROW_PATTERN, evaluated, case ):
#                 return self.get_regex( THIRD_ROW_PATTERN, evaluated, case )
#             elif self.get_regex( THIRD_ROW_PATTERN_BETA, evaluated, case ):
#                 return self.get_regex( THIRD_ROW_PATTERN_BETA, evaluated, case )
#         elif case == COMPOSITION_CODE_REGEX:
#             return self.get_regex( FOURTH_ROW_PATTERN, evaluated, case )
#         elif case == EQUIPEMENT_CODE_REGEX or case == EQUIPEMENT_QUANT_REGEX or case == EQUIPEMENT_UTIL_REGEX:
#             return self.get_regex( EQUIPEMENT_PATTERN, evaluated, case )   
#         elif case == EQUIPEMENT_QUANT_REGEX_ALFA or case == EQUIPEMENT_UTIL_REGEX_ALFA:
#             return self.get_regex( EQUIPEMENT_PATTERN_ALFA, evaluated, case )
#         elif case == EQUIPEMENT_CODE_REGEX_BETA:
#             return self.get_regex( EQUIPEMENT_PATTERN_BETA, evaluated, case )
#         elif case == GENERAL_INPUT_CODE_REGEX or case == GENERAL_INPUT_QUANT_REGEX:
#             return self.get_regex( GENERAL_INPUT_PATTERN, evaluated, case )
#         elif case == GENERAL_INPUT_QUANT_REGEX_ALFA:
#             return self.get_regex( GENERAL_INPUT_PATTERN_ALFA, evaluated, case )
#         elif case == GENERAL_INPUT_CODE_REGEX_BETA:
#             return self.get_regex( GENERAL_INPUT_PATTERN_BETA, evaluated, case )
#         elif case == FIXED_UNIT_REGEX or case == FIXED_CODE_REGEX or case == FIXED_MATERIAL_CODE_REGEX or case == FIXED_MATERIAL_QUANT_REGEX:
#             return self.get_regex( FIXED_TIME_PATTERN, evaluated, case )
#         elif case == TRANSPORTATION_UNIT_REGEX or case == TRANSPORTATION_PV_CODE_REGEX or case == TRANSPORTATION_RP_CODE_REGEX or case == TRANSPORTATION_LN_CODE_REGEX or case == TRANSPORTATION_MATERIAL_CODE_REGEX or case == TRANSPORTATION_MATERIAL_QUANT_REGEX:
#             return self.get_regex( TRANSPORTATION_PATTERN, evaluated, case )
#         elif case == BREAK_REGEX:
#             return self.get_regex( BREAK_PATTERN, evaluated, case )
#         elif case == LAST_REGEX:
#             return self.get_regex( LAST_PATTERN, evaluated, case )
#         elif case == LAST_HEADER_REGEX:
#             return self.get_regex( LAST_HEADER_PATTERN, evaluated, case )


import re

from core.usefuls.pattern import *


class CompositionRegex:

    def get_regex(
        self,
        pattern: str,
        evaluated: str,
        group: str,
    ) -> str | None:

        match = re.match(
            pattern,
            evaluated,
        )

        if match is not None:
            return match.group(group)

        return None

    def switch_regex(
        self,
        case: str,
        evaluated: str,
    ) -> str | None:

        # ========================================================
        # CABEÇALHO
        # ========================================================

        if case == FIRST_ROW_REGEX:
            return self.get_regex(
                FIRST_ROW_PATTERN,
                evaluated,
                case,
            )

        elif case == FIC_REGEX:
            return self.get_regex(
                SECOND_ROW_PATTERN,
                evaluated,
                case,
            )

        elif (
            case == DATA_BASE_REGEX
            or case == PRODUCTION_REGEX
            or case == UNIT_REGEX
        ):
            result = self.get_regex(
                THIRD_ROW_PATTERN,
                evaluated,
                case,
            )

            if result is not None:
                return result

            return self.get_regex(
                THIRD_ROW_PATTERN_BETA,
                evaluated,
                case,
            )

        elif case == COMPOSITION_CODE_REGEX:
            return self.get_regex(
                FOURTH_ROW_PATTERN,
                evaluated,
                case,
            )

        # ========================================================
        # EQUIPAMENTOS
        # ========================================================

        elif (
            case == EQUIPEMENT_CODE_REGEX
            or case == EQUIPEMENT_QUANT_REGEX
            or case == EQUIPEMENT_UTIL_REGEX
        ):
            return self.get_regex(
                EQUIPEMENT_PATTERN,
                evaluated,
                case,
            )

        elif (
            case == EQUIPEMENT_QUANT_REGEX_ALFA
            or case == EQUIPEMENT_UTIL_REGEX_ALFA
        ):
            return self.get_regex(
                EQUIPEMENT_PATTERN_ALFA,
                evaluated,
                case,
            )

        elif case == EQUIPEMENT_CODE_REGEX_BETA:
            return self.get_regex(
                EQUIPEMENT_PATTERN_BETA,
                evaluated,
                case,
            )

        # ========================================================
        # MÃO DE OBRA
        # ========================================================

        elif (
            case == WORKMANSHIP_CODE_REGEX
            or case == WORKMANSHIP_QUANT_REGEX
        ):
            return self.get_regex(
                WORKMANSHIP_PATTERN,
                evaluated,
                case,
            )

        # ========================================================
        # MATERIAIS
        # ========================================================

        elif (
            case == MATERIAL_CODE_REGEX
            or case == MATERIAL_QUANT_REGEX
        ):
            return self.get_regex(
                MATERIAL_PATTERN,
                evaluated,
                case,
            )

        elif case == MATERIAL_QUANT_REGEX_ALFA:
            return self.get_regex(
                MATERIAL_PATTERN_ALFA,
                evaluated,
                case,
            )

        elif case == MATERIAL_CODE_REGEX_BETA:
            return self.get_regex(
                MATERIAL_PATTERN_BETA,
                evaluated,
                case,
            )

        # ========================================================
        # TEMPO FIXO
        # ========================================================

        elif (
            case == FIXED_UNIT_REGEX
            or case == FIXED_CODE_REGEX
            or case == FIXED_MATERIAL_CODE_REGEX
            or case == FIXED_MATERIAL_QUANT_REGEX
        ):
            return self.get_regex(
                FIXED_TIME_PATTERN,
                evaluated,
                case,
            )

        # ========================================================
        # TRANSPORTE
        # ========================================================

        elif (
            case == TRANSPORTATION_UNIT_REGEX
            or case == TRANSPORTATION_PV_CODE_REGEX
            or case == TRANSPORTATION_RP_CODE_REGEX
            or case == TRANSPORTATION_LN_CODE_REGEX
            or case == TRANSPORTATION_MATERIAL_CODE_REGEX
            or case == TRANSPORTATION_MATERIAL_QUANT_REGEX
        ):
            return self.get_regex(
                TRANSPORTATION_PATTERN,
                evaluated,
                case,
            )

        # ========================================================
        # ATIVIDADES AUXILIARES
        # ========================================================

        elif (
            case == ACTIVITIES_CODE_REGEX
            or case == ACTIVITIES_QUANT_REGEX
        ):
            return self.get_regex(
                ACTIVITIES_PATTERN,
                evaluated,
                case,
            )

        elif case == ACTIVITIES_QUANT_REGEX_ALFA:
            return self.get_regex(
                ACTIVITIES_PATTERN_ALFA,
                evaluated,
                case,
            )

        elif case == ACTIVITIES_CODE_REGEX_BETA:
            return self.get_regex(
                ACTIVITIES_PATTERN_BETA,
                evaluated,
                case,
            )

        # ========================================================
        # CONTROLE
        # ========================================================

        elif case == BREAK_REGEX:
            return self.get_regex(
                BREAK_PATTERN,
                evaluated,
                case,
            )

        elif case == LAST_REGEX:
            return self.get_regex(
                LAST_PATTERN,
                evaluated,
                case,
            )

        elif case == LAST_HEADER_REGEX:
            return self.get_regex(
                LAST_HEADER_PATTERN,
                evaluated,
                case,
            )

        # ========================================================
        # ENTRADA GERAL
        # ========================================================

        elif (
            case == GENERAL_INPUT_CODE_REGEX
            or case == GENERAL_INPUT_QUANT_REGEX
        ):
            return self.get_regex(
                GENERAL_INPUT_PATTERN,
                evaluated,
                case,
            )

        elif case == GENERAL_INPUT_QUANT_REGEX_ALFA:
            return self.get_regex(
                GENERAL_INPUT_PATTERN_ALFA,
                evaluated,
                case,
            )

        elif case == GENERAL_INPUT_CODE_REGEX_BETA:
            return self.get_regex(
                GENERAL_INPUT_PATTERN_BETA,
                evaluated,
                case,
            )

        return None
