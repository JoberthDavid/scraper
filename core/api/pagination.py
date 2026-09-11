from rest_framework.pagination import LimitOffsetPagination


class MonetaryValuePagination(LimitOffsetPagination):
    """
    Paginação específica para valores monetários.

    ```
    O endpoint de valores monetários é utilizado pelo motor de cálculo
    para realizar o carregamento em lote dos insumos. Por isso, o
    tamanho padrão da página é elevado para reduzir o número de
    requisições HTTP.

    O limite foi definido acima da quantidade atual de registros
    retornados pelo carregamento completo do cache.
    """

    default_limit = 10000
    max_limit = 10000