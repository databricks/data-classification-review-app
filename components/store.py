import dash

token_store_id = "token-store-id"
token_store = dash.dcc.Store(id=token_store_id, storage_type="memory") 