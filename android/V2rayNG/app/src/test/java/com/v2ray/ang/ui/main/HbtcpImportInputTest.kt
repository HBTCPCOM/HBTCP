package com.v2ray.ang.ui.main

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

class HbtcpImportInputTest {
    @Test fun `empty import requires a useful validation message`() {
        assertEquals(HbtcpImportProblem.EMPTY, hbtcpImportProblem("  \n "))
    }

    @Test fun `subscription URL must have a host`() {
        assertEquals(HbtcpImportProblem.INVALID_URL, hbtcpImportProblem("https://"))
        assertEquals(HbtcpImportProblem.INVALID_URL, hbtcpImportProblem("https://bad host/sub"))
        assertNull(hbtcpImportProblem("https://example.org/sub?token=private"))
        assertNull(hbtcpImportProblem("http://10.0.2.2:8765/sub"))
    }

    @Test fun `share links JSON and base64 remain owned by protocol parsers`() {
        assertNull(hbtcpImportProblem("vless://id@example.org:443#node"))
        assertNull(hbtcpImportProblem("{\"outbounds\":[]}"))
        assertNull(hbtcpImportProblem("dmxlc3M6Ly9leGFtcGxl"))
    }
}
