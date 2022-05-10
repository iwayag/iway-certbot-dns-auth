"""API module."""

from typing import Union, Tuple
import logging
import requests
from requests import exceptions


class ApiResponseError(Exception):
    def __init__(self, message: str, status: int = None) -> None:
        super().__init__(message)
        self.status = status


class PortalApi(object):

    def __init__(self, username: str, password: str) -> None:
        self.url = 'https://backend.login.iway.ch/api'
        self.username = username
        self.password = password
        self.timeout = (5, 60)
        self.token = None
        self.login()

    def request(
            self,
            endpoint: str,
            method: str = 'get',
            ignore_json_error: bool = None,
            timeout: Union[int, Tuple[int, int]] = None,
            params: dict = None,
            data: dict = None) -> dict:
        timeout = self.timeout if timeout is None else self.timeout
        ignore_json_error = (
            False if ignore_json_error is None
            else ignore_json_error)

        try:
            url = "/".join([self.url, endpoint.lstrip('/')])
            kwargs = {
                'headers': {
                    'content-type': 'application/json',
                    'user-agent': __package__,
                },
                'timeout': timeout,
                'verify': True,
                'params': params,
                'json': data,
            }

            if self.token:
                kwargs['headers']['authorization'] = 'Bearer %s' % self.token

            func = getattr(requests, method.lower())

            # logging.getLogger(__package__).debug(
            #    "API request: %s %s %s", method, url, kwargs)

            response = func(url, **kwargs)

            if response is None:
                raise ApiResponseError("API got no response")

        except (exceptions.ConnectionError,
                exceptions.ReadTimeout,
                exceptions.RequestException) as exc:
            raise ApiResponseError(
                "API got an Error: %s" % exc) from exc

        else:
            try:
                if response.status_code >= 200 and response.status_code < 300:
                    # logging.getLogger(__package__).debug(
                    #    "API response: %s", response.json())

                    return response.json()
                else:
                    data = response.json()
                    if 'detail' in data and isinstance(data['detail'], list):
                        msg = ", ".join(data['detail'])
                    elif 'detail' in data:
                        msg = str(data['detail'])
                    else:
                        msg = str(data)
                    raise ApiResponseError(
                        "API request failed with %s: %s" % (
                            msg, response.status_code),
                        status=response.status_code)

            except ValueError as json_e:
                if response.status_code < 199 or response.status_code >= 300:
                    raise ApiResponseError(
                        "API request failed with %s: %s" % (
                            response.status_code or 0, response.text),
                        status=response.status_code) from json_e

                # response.json() raise ValueError if response contains no JSON
                # HTTP_204_NO_CONTENT will not return any JSON
                elif not ignore_json_error:
                    raise ApiResponseError(
                        "API got invalid JSON",
                        status=response.status_code) from json_e

    def login(self) -> None:
        response = self.request(
            'login',
            method='post',
            data={
                'username': self.username,
                'password': self.password
            })

        self.token = response['token']

    def get_zone(self, zone_name: str) -> dict:
        return self.request(
            'services/dns/forward/%s' % zone_name)

    def set_zone_records(self, zone_name: str, zone: dict) -> None:
        self.request(
            'services/dns/forward/%s' % zone_name,
            method='put',
            data=zone)
