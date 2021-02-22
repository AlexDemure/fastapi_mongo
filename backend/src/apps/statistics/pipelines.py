
def pipeline_for_total_data(filters: list):
    return [
        {
            '$match': {
                '$and': filters
            }
        },
        {
            '$group': {
                '_id': None,
                'total_hours': {
                    '$sum': "$hours"
                },
                'total_listeners': {
                    '$sum': "$started"
                },
                'avg_finishing': {
                    '$avg': "$finishing_rate"
                },

            }
        }
    ]


def pipeline_for_diagram(filters: list) -> list:
    return [
        {
            '$match': {
                '$and': filters
            }
        },
        {
            '$group': {
                '_id': {'uploaded_at': "$uploaded_at"},
                'total_hours': {
                    '$sum': "$hours"
                },

            }
        }
    ]


def pipeline_for_episodes(filters: list, offset: int, limit: int) -> list:
    return [
        {
            '$match': {
                '$and': filters
            }
        },
        {
            '$project': {
                'isbn': '$isbn',
                'name': '$title',
                'duration': '$duration',
                'format': '$format',
                'imprint': '$imprint',
                'author': '$author',
                'narrator': "$narrator"

            }
        },
        {
            '$skip': offset
        },
        {
            '$limit': limit
        }
    ]


def pipeline_for_analytics(filters: list, offset: int, limit: int) -> list:
    return [
        {
            '$match': {
                '$and': filters
            }
        },
        {
            '$project': {
                'isbn': '$isbn',
                'name': '$title',
                'duration': '$duration',
                'started': '$started',
                'c20': '$c20_rate',
                'c25': '$c25_rate',
                'finished': '$finishing_rate',
                'author': '$author',
                'publisher': "$publisher",
                'language': "$language",
                'pt': "$pt"
            }
        },
        {
            '$skip': offset
        },
        {
            '$limit': limit
        }
    ]
