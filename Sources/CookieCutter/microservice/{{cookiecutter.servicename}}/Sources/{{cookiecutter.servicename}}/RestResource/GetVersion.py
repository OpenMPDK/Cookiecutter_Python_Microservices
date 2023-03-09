from flask_restful import Resource, reqparse, fields
from flask_restful_swagger import swagger

from werkzeug.exceptions import BadRequest
from {{cookiecutter.servicename}}.Exception.{{cookiecutter.servicename}}Exception import {{cookiecutter.servicename}}Exception
from Utils.Errors.GenericError import GENERIC_ERR, NO_ERR
from {{cookiecutter.servicename}}.Core.{{cookiecutter.servicename}}Manager import {{cookiecutter.servicename}}Manager

class GetVersion(Resource):
    STATUS_OK = 200
    INTERNAL_SERVER_ERROR = 500

    def __init__(self):
        self._{{cookiecutter.servicename}}Manager = {{cookiecutter.servicename}}Manager.get_instance()
        self._arg_parser = reqparse.RequestParser()
        #self._arg_parser.add_argument('name', help='name of the user', required=True,location='json',dest='username',type=str)


    @swagger.operation(
        notes='API to say hello',
        nickname='hello',
        # parameters=[
        #     {
        #         'name':'body',
        #         'description':"Say hello",
        #         'required': True,
        #         'allowMultiple': False,
        #         'dataType': 'string',
        #         'paramType':'query'
        #     }
        # ],
        responseMessage = [
            {
                "code":200,
                "message":"Success"
            },
            {
                "code":500,
                "message":"Failure"
            }
        ]
    )
    def get(self):
        return_dict = dict()
        return_dict['Error_Code'] = 0
        return_dict['Message'] = None
        return_dict['Data'] = None
        return_status_code = self.STATUS_OK

        try:
            #args = self._arg_parser.parse_args()

            version  =  self._{{cookiecutter.servicename}}Manager.get_version()
            return_dict["Message"] = "Success"
            return_dict['Data'] = dict()
            return_dict['Data']['version']= version
        except {{cookiecutter.servicename}}Exception as e:
            return_dict['Error_Code'] = e.GetErrorCode()
            return_dict['Message'] = e.GetErrorMessage()
            return_dict['Data'] = None
            return_status_code = self.INTERNAL_SERVER_ERROR
        except BadRequest as e:
            return_dict['Error_Code'] = GENERIC_ERR
            return_dict['Message'] = str(e)
            return_dict['Data'] = None
            return_status_code = e.code
        except Exception as e:
            return_dict['Error_Code'] = GENERIC_ERR
            return_dict['Message'] = str(e)
            return_dict['Data'] = None
            return_status_code = self.INTERNAL_SERVER_ERROR
        return(return_dict, return_status_code)
