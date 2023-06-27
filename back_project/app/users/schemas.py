from drf_yasg import openapi
from drf_yasg.openapi import Schema, Response


RespLogin = Response('Data returned from login',
                     schema=Schema(title='ReturnedDataLogin',
                                   description='Structure of data returned from login',
                                   type='object',
                                   properties={'id': Schema(type='integer'),
                                               'name': Schema(type='string'),
                                               'last_name': Schema(type='string'),
                                               'photo': Schema(type='string'),
                                               'email': Schema(type='string'),
                                               'rol_name': Schema(description='values: Administrador, Cliente, Proveedor ',
                                                              type='string'),
                                               'created_at': Schema(type='string'),
                                               'access': Schema(description='Access token', type='string'),
                                               'refresh': Schema(description='Refresh token', type='string'),
                                               },
                                   ),
                     )


RespRefreshToken = Response('Data returned from refresh token',
                            schema=Schema(title='ReturnedDataRefreshToken',
                                          description='Structure of data returned from refresh token',
                                          type='object',
                                          properties={'access': Schema(description='Access token', type='string'),
                                                      'refresh': Schema(description='Refresh token', type='string'),
                                                      },
                                          ),
                            )
