package com.v2ray.ang.handler

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.v2ray.ang.AppConfig
import com.v2ray.ang.core.CoreConfigManager
import com.v2ray.ang.dto.entities.ProfileItem
import com.v2ray.ang.dto.entities.RulesetItem
import com.v2ray.ang.enums.EConfigType
import com.v2ray.ang.util.JsonUtil
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File

/** Only install on the dedicated QA emulator: seed methods replace its synthetic routing fixture. */
@RunWith(AndroidJUnit4::class)
class HbtcpRoutingDeviceTest {
    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    private val context = instrumentation.targetContext
    private val globalKey = "hbtcp_global_mode_v1"
    private val testGuid = "hbtcp-routing-qa"
    private val out get() = File(context.getExternalFilesDir(null), "routing-qa").apply { mkdirs() }
    private fun legacy(): MutableList<RulesetItem> = JsonUtil.fromJson(
        instrumentation.context.assets.open("hbtcp_routing_white_v1").bufferedReader().use { it.readText() },
        Array<RulesetItem>::class.java
    )!!.toMutableList()
    private fun bundled(name: String) = context.assets.open(name).bufferedReader().use { it.readText() }
    private fun custom() = legacy().apply { first().remarks = "用户保留"; first().enabled = false }
    private fun seed(rules: MutableList<RulesetItem>, global: Boolean, strategy: String?) {
        MmkvManager.encodeRoutingRulesets(rules)
        assertTrue(MmkvManager.encodeSettings(globalKey, global))
        assertTrue(MmkvManager.encodeSettings(AppConfig.PREF_ROUTING_DOMAIN_STRATEGY, strategy))
        MmkvManager.encodeServerConfig(testGuid, ProfileItem.create(EConfigType.SOCKS).apply {
            remarks = "虎斑路由验证"
            server = "10.0.2.2"
            serverPort = "19080"
        })
        MmkvManager.setSelectServer(testGuid)
    }

    @Test fun seedLegacyDefaults() = seed(legacy(), false, null)
    @Test fun seedCustomRules() = seed(custom(), false, "IPOnDemand")
    @Test fun seedGlobalRules() = seed(
        JsonUtil.fromJson(bundled("custom_routing_global"), Array<RulesetItem>::class.java)!!.toMutableList(), true, "AsIs"
    )

    @Test fun verifyDefaultUpgrade() {
        SettingsManager.updateHbtcpRoutingDefaults(context)
        SettingsManager.initAssets(context, context.assets)
        val expected = JsonUtil.fromJson(bundled("custom_routing_white"), Array<RulesetItem>::class.java)!!.toList()
        assertEquals(expected, MmkvManager.decodeRoutingRulesets())
        assertEquals("IPIfNonMatch", MmkvManager.decodeSettingsString(AppConfig.PREF_ROUTING_DOMAIN_STRATEGY))
        assertFalse(MmkvManager.decodeSettingsBool(globalKey, false))
        exportConfig("split")
        SettingsManager.updateHbtcpRoutingDefaults(context)
        assertEquals(expected, MmkvManager.decodeRoutingRulesets())
        File(out, "default-upgrade.txt").writeText("Preceding routing fixture -> current defaults; idempotent; domainStrategy=IPIfNonMatch\n")
    }

    @Test fun verifyCustomPreserved() {
        val before = MmkvManager.decodeSettingsString(AppConfig.PREF_ROUTING_RULESET)
        SettingsManager.updateHbtcpRoutingDefaults(context)
        SettingsManager.initAssets(context, context.assets)
        assertEquals(custom(), MmkvManager.decodeRoutingRulesets())
        assertEquals(before, MmkvManager.decodeSettingsString(AppConfig.PREF_ROUTING_RULESET))
        assertEquals("IPOnDemand", MmkvManager.decodeSettingsString(AppConfig.PREF_ROUTING_DOMAIN_STRATEGY))
        exportConfig("custom")
        File(out, "custom-upgrade.txt").writeText("1.0.0 custom rules and explicit strategy retained byte-for-byte\n")
    }

    @Test fun verifyGlobalPreserved() {
        val before = MmkvManager.decodeSettingsString(AppConfig.PREF_ROUTING_RULESET)
        SettingsManager.updateHbtcpRoutingDefaults(context)
        SettingsManager.initAssets(context, context.assets)
        assertEquals(before, MmkvManager.decodeSettingsString(AppConfig.PREF_ROUTING_RULESET))
        assertTrue(MmkvManager.decodeSettingsBool(globalKey, false))
        assertEquals("AsIs", MmkvManager.decodeSettingsString(AppConfig.PREF_ROUTING_DOMAIN_STRATEGY))
        exportConfig("global")
        File(out, "global-upgrade.txt").writeText("1.0.0 global rules, mode and strategy retained byte-for-byte\n")
    }

    private fun exportConfig(name: String) {
        val result = CoreConfigManager.getV2rayConfig(context, testGuid)
        assertTrue(result.errorMessage, result.status)
        val config = JsonUtil.parseString(result.content)!!
        assertEquals("proxy", config.getAsJsonArray("outbounds")[0].asJsonObject["tag"].asString)
        File(out, "$name-config.json").writeText(result.content)
    }
}
