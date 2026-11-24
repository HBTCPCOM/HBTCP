package com.v2ray.ang.handler

import com.v2ray.ang.AppConfig
import com.v2ray.ang.dto.entities.RulesetItem
import com.v2ray.ang.util.JsonUtil
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import java.io.File

class HubanRoutingUpgradeTest {
    private val assets = File("src/main/assets")
    private fun rules(name: String) = JsonUtil.fromJson(
        File(assets, name).readText(), Array<RulesetItem>::class.java
    )!!.toList()
    private val legacy = rules("huban_routing_white_v1")
    private val preset = rules("custom_routing_white")

    @Test
    fun `preceding default labels receive HBTCP branding without changing route conditions`() {
        val previous = rules("huban_routing_white_v2")
        val updates = SettingsManager.planHubanRoutingUpgrade(previous, legacy, preset, "IPIfNonMatch", previous)
        assertEquals(JsonUtil.toJson(preset), updates[AppConfig.PREF_ROUTING_RULESET])
        assertFalse(updates.containsKey(AppConfig.PREF_ROUTING_DOMAIN_STRATEGY))
        assertEquals(previous.map { it.copy(remarks = "") }, preset.map { it.copy(remarks = "") })
    }

    @Test
    fun `custom labels in the preceding release remain user data`() {
        val previous = rules("huban_routing_white_v2")
        val custom = previous.mapIndexed { i, r -> if (i == 0) r.copy(remarks = "Mine") else r }
        assertTrue(SettingsManager.planHubanRoutingUpgrade(custom, legacy, preset, "AsIs", previous).isEmpty())
    }

    @Test
    fun `upgrades the preceding release format and initializes IP fallback once`() {
        val updates = SettingsManager.planHubanRoutingUpgrade(legacy, legacy, preset, null)
        assertEquals(preset, JsonUtil.fromJson(updates[AppConfig.PREF_ROUTING_RULESET]!!, Array<RulesetItem>::class.java)!!.toList())
        assertEquals("IPIfNonMatch", updates[AppConfig.PREF_ROUTING_DOMAIN_STRATEGY])
        assertTrue(SettingsManager.planHubanRoutingUpgrade(preset, legacy, preset, "IPIfNonMatch").isEmpty())
    }

    @Test
    fun `fresh defaults initialize strategy without replacing rules`() {
        val updates = SettingsManager.planHubanRoutingUpgrade(preset, legacy, preset, null)
        assertEquals(mapOf(AppConfig.PREF_ROUTING_DOMAIN_STRATEGY to "IPIfNonMatch"), updates)
    }

    @Test
    fun `preserves every explicitly saved DNS routing strategy including AsIs`() {
        listOf("AsIs", "IPOnDemand", "IPIfNonMatch").forEach { strategy ->
            val updates = SettingsManager.planHubanRoutingUpgrade(legacy, legacy, preset, strategy)
            assertNotNull(updates[AppConfig.PREF_ROUTING_RULESET])
            assertFalse(updates.containsKey(AppConfig.PREF_ROUTING_DOMAIN_STRATEGY))
        }
    }

    @Test
    fun `preserves custom order content flags IDs and global rules`() {
        val custom = listOf(
            legacy.reversed(), legacy.drop(1), emptyList(), rules("custom_routing_global"),
            legacy.mapIndexed { i, r -> if (i == 0) r.copy(enabled = false) else r },
            legacy.mapIndexed { i, r -> if (i == 0) r.copy(locked = true) else r },
            legacy.mapIndexed { i, r -> if (i == 0) r.copy(id = "user-id") else r },
            legacy.mapIndexed { i, r -> if (i == 0) r.copy(remarks = "Mine") else r },
            legacy + RulesetItem(domain = listOf("domain:example.com"), outboundTag = "direct"),
        )
        custom.forEach { current ->
            assertTrue(SettingsManager.planHubanRoutingUpgrade(current, legacy, preset, null).isEmpty())
        }
    }

    @Test
    fun `restores both records if encoding returns false or throws`() {
        for (failureAt in 1..2) for (throwFailure in listOf(false, true)) {
            val storage = mutableMapOf<String, String?>("rules" to "old")
            val original = storage.toMap()
            var writes = 0
            assertThrows(IllegalStateException::class.java) {
                SettingsManager.commitRoutingUpgrade(mapOf("rules" to "new", "strategy" to "IPIfNonMatch"), storage::get) { key, value ->
                    writes++
                    if (value == null) storage.remove(key) else storage[key] = value
                    if (writes == failureAt) {
                        if (throwFailure) error("write failure")
                        false
                    } else true
                }
            }
            assertEquals(original, storage)
        }
    }

    @Test
    fun `keeps site domain semantics and all local CIDRs in their original order`() {
        val source = File("../../routing/hbtcp-shadowrocket.conf").readText().substringAfter("[Rule]")
        val explicit = source.lines().filter { it.startsWith("DOMAIN,") || it.startsWith("DOMAIN-SUFFIX,") }
        for (line in explicit) {
            val (kind, value, target) = line.split(',')
            val domain = (if (kind == "DOMAIN") "full:" else "domain:") + value
            val match = preset.single { it.domain?.contains(domain) == true }
            assertEquals(if (target == "DIRECT") "direct" else "proxy", match.outboundTag)
        }
        val cidrs = source.lines().filter { it.startsWith("IP-CIDR,") || it.startsWith("IP-CIDR6,") }.map { it.split(',')[1] }
        assertEquals(listOf("geoip:private") + cidrs, preset[3].ip)
        assertEquals(listOf("geoip:cn"), preset.last().ip)
        assertTrue(preset.take(3).all { !it.domain.isNullOrEmpty() && it.ip == null })
        // Xray must exhaust the first pass to trigger IPIfNonMatch. Its first outbound is the final proxy.
        assertTrue(preset.all { it.port == null && it.network == null })
        assertTrue(preset.any { it.domain?.contains("geosite:private") == true })
        assertEquals(71, explicit.size)
    }
}
