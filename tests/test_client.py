# -*- coding: utf-8 -*-
import unittest

from axisvm.com.client import start_AxisVM
from axisvm.com.tlb import lbTrue as true, lbFalse as false, \
    acEnableNoWarning


class TestClient(unittest.TestCase):

    def test_client(self):
        axvm = start_AxisVM(visible=False)
        axvm.CloseOnLastReleased = true
        axvm.AskCloseOnLastReleased = false
        axvm.AskSaveOnLastReleased = false
        axvm.ApplicationClose = acEnableNoWarning
        modelId = axvm.Models.New()
        axm = axvm.Models.Item[modelId]
        #axvm.UnLoadCOMClients()
        axvm.Quit(unload_client=False)
           
                  
if __name__ == "__main__":
    unittest.main()  # pragma: no cover
