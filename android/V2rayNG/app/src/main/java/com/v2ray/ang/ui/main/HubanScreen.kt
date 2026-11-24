package com.v2ray.ang.ui.main

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.consumeWindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.v2ray.ang.R
import com.v2ray.ang.dto.entities.ServersCache
import com.v2ray.ang.ui.compose.LocalDarkTheme

private data class HubanColors(
    val background: Color,
    val hero: Color,
    val ink: Color,
    val secondary: Color,
    val inset: Color,
    val line: Color,
    val selected: Color,
    val onSelected: Color,
    val actionText: Color = Color(0xFF9C4F00),
    val orange: Color = Color(0xFFFC8903),
    val onOrange: Color = Color(0xFF24190C),
    val connected: Color
)

@Composable
private fun hubanColors(): HubanColors = if (LocalDarkTheme.current) {
    HubanColors(
        Color(0xFF24211D), Color(0xFF3D2E1B), Color(0xFFF6F0E5),
        Color(0xFFC2B7A5), Color(0xFF312D26), Color(0x22FCEFD9),
        Color(0xFFEEE4D3), Color(0xFF30291F), actionText = Color(0xFFFFB464), connected = Color(0xFF83C7A2)
    )
} else {
    HubanColors(
        Color(0xFFFFFDF8), Color(0xFFFFE9C8), Color(0xFF29251E),
        Color(0xFF746A5A), Color(0xFFF3F0E9), Color(0x193F2A11),
        Color(0xFF30291F), Color(0xFFFFF8EE), connected = Color(0xFF307151)
    )
}

/** The compact Huban entry uses the existing main-screen action, repository and daemon contracts. */
@Composable
fun HubanScreen(
    viewModel: MainViewModel,
    onAction: (MainAction) -> Unit,
    onNavigate: (MainDestination) -> Unit
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val loading by viewModel.isLoading.collectAsStateWithLifecycle()
    val servers by viewModel.serversForGroup(state.selectedGroupId).collectAsStateWithLifecycle()
    val colors = hubanColors()
    var importMenu by rememberSaveable { mutableStateOf(false) }
    var appMenu by rememberSaveable { mutableStateOf(false) }
    var importDialog by rememberSaveable { mutableStateOf(false) }
    var nodeDialog by rememberSaveable { mutableStateOf(false) }
    var subscriptionDialog by rememberSaveable { mutableStateOf(false) }
    var input by rememberSaveable { mutableStateOf("") }
    var importStarted by rememberSaveable { mutableStateOf(false) }
    val selected = servers.firstOrNull { it.guid == state.selectedGuid }
    val group = state.groups.firstOrNull { it.id == state.selectedGroupId }

    LaunchedEffect(state.hubanImportRevision) {
        if (importStarted && state.hubanImportRevision > 0) {
            importDialog = false
            importStarted = false
            input = ""
        }
    }

    Scaffold(
        containerColor = colors.background,
        bottomBar = {
            Surface(color = colors.background) {
                Column(Modifier.fillMaxWidth().navigationBarsPadding().padding(horizontal = 26.dp).padding(top = 8.dp, bottom = 12.dp)) {
                    Button(
                        onClick = {
                            when (hubanConnectionAction(state.isRunning, servers.isNotEmpty(), selected != null)) {
                                HubanConnectionAction.IMPORT -> importDialog = true
                                HubanConnectionAction.SELECT_NODE -> nodeDialog = true
                                HubanConnectionAction.START, HubanConnectionAction.STOP -> onAction(MainAction.ToggleService)
                            }
                        },
                        enabled = !loading,
                        modifier = Modifier.fillMaxWidth().height(58.dp),
                        shape = RoundedCornerShape(17.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = if (state.isRunning) colors.selected else colors.orange,
                            contentColor = if (state.isRunning) colors.onSelected else colors.onOrange,
                            disabledContainerColor = colors.inset,
                            disabledContentColor = colors.secondary
                        )
                    ) {
                        if (loading) CircularProgressIndicator(Modifier.size(20.dp), color = colors.secondary, strokeWidth = 2.dp)
                        else Icon(painterResource(R.drawable.huban_power), null, Modifier.size(22.dp))
                        Spacer(Modifier.width(11.dp))
                        Text(stringResource(if (loading) R.string.huban_importing else if (state.isRunning) R.string.huban_disconnect else R.string.huban_start), fontSize = 17.sp, fontWeight = FontWeight.SemiBold)
                    }
                }
            }
        }
    ) { padding ->
        BoxWithConstraints(
            Modifier.fillMaxSize().padding(padding).consumeWindowInsets(padding)
        ) {
            val compact = maxHeight < 680.dp
            Column(
                Modifier.fillMaxSize().verticalScroll(rememberScrollState()).imePadding()
            ) {
                Column(
                    Modifier.fillMaxWidth().clip(RoundedCornerShape(bottomStart = 32.dp, bottomEnd = 32.dp))
                        .background(colors.hero).padding(horizontal = 26.dp).padding(top = 8.dp, bottom = 14.dp)
                ) {
                    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                        Column(Modifier.weight(1f)) {
                            Text(stringResource(R.string.app_name), color = colors.ink, fontSize = 24.sp, fontWeight = FontWeight.ExtraBold, letterSpacing = 1.sp)
                        }
                        Box(Modifier.size(6.dp).background(if (state.isRunning) colors.connected else colors.secondary, CircleShape))
                        Spacer(Modifier.width(7.dp))
                        Text(stringResource(if (state.isRunning) R.string.huban_connected else R.string.huban_disconnected), color = if (state.isRunning) colors.connected else colors.secondary, fontSize = 12.sp)
                        Box {
                            IconButton(onClick = { appMenu = true }, modifier = Modifier.size(48.dp)) {
                                Icon(painterResource(R.drawable.ic_settings_24dp), stringResource(R.string.title_settings), tint = colors.secondary, modifier = Modifier.size(21.dp))
                            }
                            DropdownMenu(
                                expanded = appMenu, onDismissRequest = { appMenu = false },
                                modifier = Modifier.width(228.dp), shape = RoundedCornerShape(20.dp),
                                containerColor = colors.background, tonalElevation = 0.dp, shadowElevation = 8.dp,
                                border = BorderStroke(1.dp, colors.line)
                            ) {
                                Text(stringResource(R.string.title_settings), color = colors.secondary, fontSize = 11.sp, fontWeight = FontWeight.Medium, modifier = Modifier.padding(start = 20.dp, top = 8.dp, bottom = 6.dp))
                                HubanMenuItem(R.string.huban_refresh, R.drawable.ic_refresh_24dp, colors) { appMenu = false; onAction(MainAction.UpdateSubscriptions) }
                                HubanMenuItem(R.string.huban_manage_subscriptions, R.drawable.ic_subscriptions_24dp, colors) { appMenu = false; onNavigate(MainDestination.Subscriptions) }
                                HorizontalDivider(Modifier.padding(horizontal = 18.dp, vertical = 5.dp), color = colors.line)
                                HubanMenuItem(R.string.huban_logs, R.drawable.ic_logcat_24dp, colors) { appMenu = false; onNavigate(MainDestination.Logcat) }
                                HubanMenuItem(R.string.huban_about, R.drawable.ic_about_24dp, colors) { appMenu = false; onNavigate(MainDestination.About) }
                            }
                        }
                    }
                    Spacer(Modifier.height(if (compact) 4.dp else 10.dp))
                    Image(painterResource(R.drawable.huban_logo), null, Modifier.size(if (compact) 104.dp else 136.dp).align(Alignment.CenterHorizontally))
                }
                Column(Modifier.fillMaxWidth().padding(horizontal = 26.dp).padding(top = if (compact) 14.dp else 18.dp, bottom = 10.dp)) {
                    Text(
                        stringResource(if (state.isRunning) R.string.huban_departed else R.string.huban_ready),
                        color = colors.ink, fontSize = 26.sp, fontWeight = FontWeight.SemiBold,
                        modifier = Modifier.align(Alignment.CenterHorizontally)
                    )
                    Spacer(Modifier.height(6.dp))
                    Text(stringResource(if (state.isRunning) R.string.huban_connected_hint else R.string.huban_ready_hint), color = colors.secondary, fontSize = 13.sp, modifier = Modifier.align(Alignment.CenterHorizontally))
                    Spacer(Modifier.height(if (compact) 16.dp else 22.dp))
                    HubanLabel(R.string.huban_mode, colors)
                    Row(Modifier.fillMaxWidth().background(colors.inset, RoundedCornerShape(15.dp)).padding(4.dp)) {
                        HubanModeButton(R.string.huban_rule, R.drawable.huban_split, !state.hubanGlobalMode, colors, Modifier.weight(1f)) { onAction(MainAction.SetHubanGlobalMode(false)) }
                        HubanModeButton(R.string.huban_global, R.drawable.huban_globe, state.hubanGlobalMode, colors, Modifier.weight(1f)) { onAction(MainAction.SetHubanGlobalMode(true)) }
                    }
                    Spacer(Modifier.height(8.dp))
                    Text(stringResource(if (state.hubanGlobalMode) R.string.huban_global_hint else R.string.huban_rule_hint), color = colors.secondary, fontSize = 12.sp, lineHeight = 19.sp)
                    Spacer(Modifier.height(16.dp))
                    HubanLabel(R.string.huban_subscription, colors)
                    Row(
                        Modifier.fillMaxWidth().heightIn(min = 70.dp)
                            .background(colors.background, RoundedCornerShape(16.dp))
                            .then(Modifier.clip(RoundedCornerShape(16.dp)))
                            .background(colors.line).padding(1.dp)
                            .background(colors.background, RoundedCornerShape(15.dp)),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            Modifier.weight(1f).clickable { if (state.groups.count { it.id.isNotEmpty() } > 1) subscriptionDialog = true else importDialog = true }
                                .padding(start = 14.dp, top = 14.dp, bottom = 14.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Box(Modifier.size(38.dp).background(colors.inset, RoundedCornerShape(12.dp)), contentAlignment = Alignment.Center) {
                                Icon(painterResource(R.drawable.huban_link), null, tint = colors.secondary, modifier = Modifier.size(18.dp))
                            }
                            Spacer(Modifier.width(12.dp))
                            Column(Modifier.weight(1f)) {
                                Text(if (servers.isEmpty()) stringResource(R.string.huban_import_link) else group?.remarks?.takeIf { it.isNotBlank() && it != "import sub" } ?: stringResource(R.string.huban_imported), color = colors.ink, fontSize = 15.sp, fontWeight = FontWeight.Medium, maxLines = 1, overflow = TextOverflow.Ellipsis)
                                Spacer(Modifier.height(4.dp))
                                Text(if (loading) stringResource(R.string.huban_importing) else if (servers.isEmpty()) stringResource(R.string.huban_import_methods) else stringResource(R.string.huban_node_count, servers.size), color = colors.secondary, fontSize = 12.sp, maxLines = 1)
                            }
                        }
                        Box {
                            IconButton(onClick = { importMenu = true }, enabled = !loading, modifier = Modifier.size(46.dp)) {
                                Icon(painterResource(R.drawable.ic_expand_more_24dp), stringResource(R.string.huban_import_options), tint = colors.secondary, modifier = Modifier.size(20.dp))
                            }
                            DropdownMenu(
                                expanded = importMenu, onDismissRequest = { importMenu = false },
                                modifier = Modifier.width(244.dp), shape = RoundedCornerShape(20.dp),
                                containerColor = colors.background, tonalElevation = 0.dp, shadowElevation = 8.dp,
                                border = BorderStroke(1.dp, colors.line)
                            ) {
                                Text(stringResource(R.string.huban_import_options), color = colors.secondary, fontSize = 11.sp, fontWeight = FontWeight.Medium, modifier = Modifier.padding(start = 20.dp, top = 8.dp, bottom = 6.dp))
                                HubanMenuItem(R.string.huban_import_link, R.drawable.huban_link, colors) { importMenu = false; importDialog = true }
                                HubanMenuItem(R.string.huban_scan, R.drawable.ic_scan_24dp, colors) { importMenu = false; onAction(MainAction.ImportQRcode) }
                                HubanMenuItem(R.string.huban_clipboard, R.drawable.ic_copy, colors) { importMenu = false; onAction(MainAction.ImportClipboard) }
                            }
                        }
                    }
                    if (state.hubanImportError != null && !importDialog) {
                        Text(stringResource(state.hubanImportError!!), color = MaterialTheme.colorScheme.error, fontSize = 12.sp, modifier = Modifier.padding(top = 8.dp))
                    }
                    Spacer(Modifier.height(16.dp))
                    HubanLabel(R.string.huban_node, colors)
                    Surface(
                        onClick = { if (servers.isNotEmpty()) nodeDialog = true else importDialog = true },
                        modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(15.dp),
                        color = if (servers.isEmpty()) colors.inset else colors.background,
                        border = BorderStroke(1.dp, colors.line)
                    ) {
                        Row(Modifier.heightIn(min = 52.dp).padding(horizontal = 15.dp, vertical = 13.dp), verticalAlignment = Alignment.CenterVertically) {
                            Text(selected?.profile?.remarks?.takeIf { it.isNotBlank() } ?: stringResource(R.string.huban_select_after_import), color = if (servers.isEmpty()) colors.secondary else colors.ink, fontSize = 15.sp, modifier = Modifier.weight(1f), maxLines = 1, overflow = TextOverflow.Ellipsis)
                            Icon(painterResource(R.drawable.ic_expand_more_24dp), null, tint = colors.secondary, modifier = Modifier.size(20.dp))
                        }
                    }
                    Text(stringResource(R.string.huban_switch_hint), color = colors.secondary, fontSize = 12.sp, lineHeight = 19.sp, modifier = Modifier.padding(top = 8.dp))
                }
            }
        }
    }

    if (importDialog) {
        AlertDialog(
            onDismissRequest = { if (!loading) { importDialog = false; onAction(MainAction.DismissHubanImportError) } },
            title = { Text(stringResource(R.string.huban_import_link)) },
            text = {
                Column(Modifier.verticalScroll(rememberScrollState()).imePadding()) {
                    OutlinedTextField(
                        value = input,
                        onValueChange = { input = it; onAction(MainAction.DismissHubanImportError) },
                        label = { Text(stringResource(R.string.huban_subscription_url)) },
                        modifier = Modifier.fillMaxWidth(), enabled = !loading,
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri),
                        minLines = 2, maxLines = 5,
                        isError = state.hubanImportError != null
                    )
                    Spacer(Modifier.height(8.dp))
                    Text(stringResource(state.hubanImportError ?: R.string.huban_import_help), color = if (state.hubanImportError == null) colors.secondary else MaterialTheme.colorScheme.error, fontSize = 12.sp, lineHeight = 19.sp)
                }
            },
            confirmButton = {
                TextButton(enabled = !loading, colors = ButtonDefaults.textButtonColors(contentColor = colors.actionText), onClick = { importStarted = true; onAction(MainAction.ImportBatchConfig(input)) }) {
                    Text(stringResource(if (loading) R.string.huban_importing else R.string.huban_import))
                }
            },
            dismissButton = { TextButton(enabled = !loading, colors = ButtonDefaults.textButtonColors(contentColor = colors.secondary), onClick = { importDialog = false; onAction(MainAction.DismissHubanImportError) }) { Text(stringResource(R.string.huban_cancel)) } },
            containerColor = colors.background
        )
    }
    if (nodeDialog) {
        HubanNodeDialog(servers, state.selectedGuid, colors, onDismiss = { nodeDialog = false }) { guid ->
            nodeDialog = false
            onAction(MainAction.SelectServer(guid))
        }
    }
    if (subscriptionDialog) {
        AlertDialog(
            onDismissRequest = { subscriptionDialog = false },
            title = { Text(stringResource(R.string.huban_subscription)) },
            text = {
                Column(Modifier.heightIn(max = 400.dp).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    state.groups.forEach { item ->
                        androidx.compose.runtime.key(item.id) {
                            val isSelected = item.id == state.selectedGroupId
                            Surface(
                                onClick = { onAction(MainAction.SelectGroup(item.id)); subscriptionDialog = false },
                                modifier = Modifier.fillMaxWidth().semantics { this.selected = isSelected; this.role = Role.RadioButton }, shape = RoundedCornerShape(14.dp),
                                color = if (isSelected) colors.inset else colors.background,
                                border = BorderStroke(1.dp, colors.line)
                            ) {
                                Row(Modifier.padding(horizontal = 14.dp, vertical = 15.dp), verticalAlignment = Alignment.CenterVertically) {
                                    Icon(painterResource(R.drawable.huban_link), null, tint = colors.secondary, modifier = Modifier.size(19.dp))
                                    Spacer(Modifier.width(12.dp))
                                    Text(item.remarks, color = colors.ink, fontSize = 14.sp, modifier = Modifier.weight(1f), maxLines = 2, overflow = TextOverflow.Ellipsis)
                                    if (isSelected) Icon(painterResource(R.drawable.ic_action_done), null, tint = colors.actionText, modifier = Modifier.size(18.dp))
                                }
                            }
                        }
                    }
                }
            },
            confirmButton = { TextButton(colors = ButtonDefaults.textButtonColors(contentColor = colors.actionText), onClick = { subscriptionDialog = false; importDialog = true }) { Text(stringResource(R.string.huban_import_link)) } },
            dismissButton = { TextButton(colors = ButtonDefaults.textButtonColors(contentColor = colors.secondary), onClick = { subscriptionDialog = false }) { Text(stringResource(R.string.huban_cancel)) } },
            containerColor = colors.background
        )
    }
}

@Composable
private fun HubanMenuItem(text: Int, icon: Int, colors: HubanColors, onClick: () -> Unit) {
    DropdownMenuItem(
        text = { Text(stringResource(text), color = colors.ink, fontSize = 14.sp, fontWeight = FontWeight.Medium) },
        leadingIcon = {
            Box(Modifier.size(32.dp).background(colors.inset, RoundedCornerShape(10.dp)), contentAlignment = Alignment.Center) {
                Icon(painterResource(icon), null, tint = colors.secondary, modifier = Modifier.size(18.dp))
            }
        },
        modifier = Modifier.padding(horizontal = 6.dp).heightIn(min = 52.dp).clip(RoundedCornerShape(13.dp)),
        onClick = onClick
    )
}

@Composable
private fun HubanLabel(text: Int, colors: HubanColors) {
    Text(stringResource(text), color = colors.secondary, fontSize = 12.sp, fontWeight = FontWeight.Medium, modifier = Modifier.padding(bottom = 7.dp))
}

@Composable
private fun HubanModeButton(text: Int, icon: Int, selected: Boolean, colors: HubanColors, modifier: Modifier, onClick: () -> Unit) {
    Row(
        modifier.height(44.dp).clip(RoundedCornerShape(12.dp))
            .background(if (selected) colors.selected else Color.Transparent)
            .selectable(selected = selected, role = Role.RadioButton, onClick = onClick),
        verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.Center
    ) {
        Icon(painterResource(icon), null, tint = if (selected) colors.onSelected else colors.secondary, modifier = Modifier.size(18.dp))
        Spacer(Modifier.width(8.dp))
        Text(stringResource(text), fontSize = 15.sp, fontWeight = FontWeight.Medium, color = if (selected) colors.onSelected else colors.secondary)
    }
}

@Composable
private fun HubanNodeDialog(servers: List<ServersCache>, selectedGuid: String?, colors: HubanColors, onDismiss: () -> Unit, onSelect: (String) -> Unit) {
    val focusRequester = remember { FocusRequester() }
    val focusTarget = servers.firstOrNull { it.guid == selectedGuid }?.guid ?: servers.firstOrNull()?.guid
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(stringResource(R.string.huban_select_node)) },
        text = {
            Column(Modifier.heightIn(max = 420.dp).verticalScroll(rememberScrollState())) {
                servers.forEach { server ->
                    androidx.compose.runtime.key(server.guid) {
                        val selected = server.guid == selectedGuid
                        Row(
                            Modifier.fillMaxWidth().heightIn(min = 56.dp)
                                .then(if (server.guid == focusTarget) Modifier.focusRequester(focusRequester) else Modifier)
                                .clip(RoundedCornerShape(12.dp))
                                .background(if (selected) colors.inset else Color.Transparent)
                                .selectable(selected = selected, role = Role.RadioButton, onClick = { onSelect(server.guid) })
                                .padding(horizontal = 12.dp, vertical = 13.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(server.profile.remarks.orEmpty().ifEmpty { server.profile.configType.name }, fontSize = 14.sp, color = colors.ink, modifier = Modifier.weight(1f), maxLines = 2, overflow = TextOverflow.Ellipsis)
                            if (selected) Icon(painterResource(R.drawable.ic_action_done), null, Modifier.size(18.dp).clearAndSetSemantics { }, tint = colors.connected)
                        }
                    }
                }
                LaunchedEffect(focusTarget, servers.map { it.guid }) {
                    if (focusTarget != null) focusRequester.requestFocus()
                }
            }
        },
        confirmButton = { TextButton(colors = ButtonDefaults.textButtonColors(contentColor = colors.actionText), onClick = onDismiss) { Text(stringResource(R.string.huban_close)) } },
        containerColor = colors.background
    )
}
