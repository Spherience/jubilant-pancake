import json
import bson.json_util as json_util

def json_fy(obj):
  return json.loads(json_util.dumps(obj))