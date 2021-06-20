#!/usr/bin/env python3
#
# Copyright (c) 2019 Roberto Riggio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

"""MEC Manager."""

import json

from tornado.httpclient import AsyncHTTPClient

from empower_core.launcher import srv_or_die
from empower_core.serialize import serialize
from empower_core.service import EService
from lightedge_core.subscription import Subscription

DEFAULT_REGISTRY = "http://127.0.0.1:8887/api/v1/services"


class MECManager(EService):
    """MEC Microservice baseclass."""

    SUBSCRIPTIONS = {}

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.state = "UNREGISTERED"

    @property
    def registry(self):
        """Return registry."""

        return self.params["registry"]

    @registry.setter
    def registry(self, value):
        """Set registry."""

        if "registry" in self.params and self.params["registry"]:
            raise ValueError("Param registry can not be changed")

        self.params["registry"] = str(value)

    async def get(self, url):
        """REST get method."""

        http_client = AsyncHTTPClient()
        response = await http_client.fetch(url, raise_error=False)

        return response

    async def post(self, url, data):
        """Test post method."""

        data["version"] = "1.0"

        http_client = AsyncHTTPClient()

        response = await http_client.fetch(url,
                                           method='POST',
                                           body=json.dumps(data),
                                           raise_error=False)

        return response

    @property
    def subscriptions(self):
        """Return subscriptions."""

        subscriptions = {}

        for service in srv_or_die("envmanager").env.services.values():

            if not isinstance(service, Subscription):
                continue

            subscriptions[service.service_id] = service

        return subscriptions

    def get_subscriptions_links(self):
        """Return subscriptions."""

        href = self.mec_service['serCategory']['href']

        out = {
            "_links": {
                "self": "%s/subscriptions" % href,
                "subscription": []
            }
        }

        for sub in self.subscriptions.values():

            to_add = {
                "href": "%s/subscriptions/%s" % (href, sub.service_id),
                "subscriptionType": sub.SUB_CONFIG
            }

            out["_links"]["subscription"].append(to_add)

        return out

    def add_subscription(self, sub_id, params):
        """Add a new subscription."""

        if sub_id in self.subscriptions:
            raise ValueError("Subscription %s already defined" % sub_id)

        name = self.SUBSCRIPTIONS[params['subscriptionType']]

        print(name)
        params = {
            "subscription": params
        }

        env = srv_or_die("envmanager").env
        sub = env.register_service(name=name,
                                   params=params,
                                   service_id=sub_id)

        sub.add_callback(sub.callback_reference, callback_type="rest")

        return sub

    def rem_subscription(self, sub_id=None):
        """Remove subscription."""

        env = srv_or_die("envmanager").env

        if sub_id:
            service_id = self.subscriptions[sub_id].service_id
            env.unregister_service(service_id=service_id)
        else:
            for service_id in self.subscriptions:
                env.unregister_service(service_id=service_id)

    def to_dict(self):
        """Return JSON representation."""

        output = super().to_dict()

        output['mec_service'] = self.mec_service

        return output

    @property
    def mec_service(self):
        """Return subscriptions."""

        raise ValueError("Not Implemented")

    async def loop(self):
        """Periodic job."""

        try:
            await self.register()
        except ConnectionRefusedError:
            self.log.error("Unable to contact MEC service registry")

    async def register(self):
        """Register MEC service."""

        http_client = AsyncHTTPClient()

        url = self.registry + "/" + str(self.service_id)
        body = serialize(self.mec_service)

        response = await http_client.fetch(url, method='POST',
                                           body=json.dumps(body),
                                           raise_error=False)

        if response.code == 201:
            self.state = "REGISTERED"
        else:
            self.state = "UNREGISTERED"

        self.log.info("Sending periodic keep-alive, response %u",
                      response.code)
