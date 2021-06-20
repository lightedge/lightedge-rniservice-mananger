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

"""RNIS Manager."""

import json

from tornado.httpclient import AsyncHTTPClient

from empower_core.appworker import EVERY
from empower_core.launcher import srv_or_die

from lightedge_core.mecmanager import DEFAULT_REGISTRY
from lightedge_core.mecmanager import MECManager
from lightedge_core.subscription import Subscription
from lightedge_core.subscriptionshandler import SubscriptionsHandler
from lightedge_core.subscriptionscallbackhandler \
    import SubscriptionsCallbackHandler

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8888
DEFAULT_USER = "root"
DEFAULT_PWD = "root"


class RNISManager(MECManager):
    """Service exposing the RNI service."""

    HANDLERS = [SubscriptionsHandler, SubscriptionsCallbackHandler]

    SUBSCRIPTIONS = {
        "MeasRepUeSubscription":
            "lightedge_rniservice_manager.workers.measrepue.measrepue"
    }

    def __init__(self, context, service_id, ctrl_host, ctrl_port,
                 ctrl_user, ctrl_pwd, registry, every=EVERY):

        super().__init__(context=context, service_id=service_id,
                         ctrl_host=ctrl_host, ctrl_port=ctrl_port,
                         ctrl_user=ctrl_user, ctrl_pwd=ctrl_pwd,
                         registry=registry, every=every)

    @property
    def mec_service(self):
        """Return MEC service descriptor."""

        return {
            "serInstanceId": self.service_id,
            "serName": "Radio Network Information Service",
            "serCategory": {
                "href": "/rni/v2/",
                "id": "rni",
                "name": "Radio Network Information Service",
                "version": "2.0"
            },
            "version": "1.0",
            "state": self.state,
            "serializer": "JSON",
        }

    @property
    def empower_url(self):
        """Return empower URL."""

        params = (self.ctrl_user, self.ctrl_pwd, self.ctrl_host,
                  self.ctrl_port)

        return "http://%s:%s@%s:%u/api/v1" % params

    @property
    def ctrl_host(self):
        """Return ctrl_host."""

        return self.params["ctrl_host"]

    @ctrl_host.setter
    def ctrl_host(self, value):
        """Set ctrl_host."""

        if "ctrl_host" in self.params and self.params["ctrl_host"]:
            raise ValueError("Param ctrl_host can not be changed")

        self.params["ctrl_host"] = str(value)

    @property
    def ctrl_port(self):
        """Return ctrl_port."""

        return self.params["ctrl_port"]

    @ctrl_port.setter
    def ctrl_port(self, value):
        """Set ctrl_port."""

        if "ctrl_port" in self.params and self.params["ctrl_port"]:
            raise ValueError("Param ctrl_port can not be changed")

        self.params["ctrl_port"] = int(value)

    @property
    def ctrl_user(self):
        """Return ctrl_user."""

        return self.params["ctrl_user"]

    @ctrl_user.setter
    def ctrl_user(self, value):
        """Set ctrl_user."""

        if "ctrl_user" in self.params and self.params["ctrl_user"]:
            raise ValueError("Param ctrl_user can not be changed")

        self.params["ctrl_user"] = value

    @property
    def ctrl_pwd(self):
        """Return ctrl_pwd."""

        return self.params["ctrl_pwd"]

    @ctrl_pwd.setter
    def ctrl_pwd(self, value):
        """Set ctrl_pwd."""

        if "ctrl_pwd" in self.params and self.params["ctrl_pwd"]:
            raise ValueError("Param ctrl_pwd can not be changed")

        self.params["ctrl_pwd"] = value


def launch(context, service_id, ctrl_host=DEFAULT_HOST,
           ctrl_port=DEFAULT_PORT, ctrl_user=DEFAULT_USER,
           ctrl_pwd=DEFAULT_PWD, registry=DEFAULT_REGISTRY, every=EVERY):
    """ Initialize the module. """

    return RNISManager(context, service_id, ctrl_host, ctrl_port, ctrl_user,
                       ctrl_pwd, registry, every)
