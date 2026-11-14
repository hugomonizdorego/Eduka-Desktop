// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
// Round button of the rail beside the login cards (0.11 RC3): an icon, a
// short caption under it (language or keyboard layout) and a tooltip.
import QtQuick 2.15

Rectangle {
    id: button
    property var theme
    property string icon: ""
    property string caption: ""
    property string tip: ""
    property bool active: false
    property bool open: false
    signal activated()

    readonly property bool hot: area.containsMouse || open || activeFocus
    width: 44 * theme.s
    height: caption.length > 0 ? 54 * theme.s : 44 * theme.s
    radius: width / 2
    color: area.pressed ? Qt.darker(theme.accent, 1.12) : (hot ? theme.accent : (active ? theme.hoverColor : "transparent"))
    border.color: active && !hot ? theme.accent : "transparent"
    border.width: active && !hot ? 1.5 : 0
    activeFocusOnTab: true
    Behavior on color { ColorAnimation { duration: 120 } }
    Accessible.role: Accessible.Button
    Accessible.name: tip
    Accessible.onPressAction: button.activated()
    Keys.onReturnPressed: button.activated()
    Keys.onSpacePressed: button.activated()

    Icon {
        id: glyph
        anchors.horizontalCenter: parent.horizontalCenter
        y: button.caption.length > 0 ? 9 * button.theme.s : (parent.height - height) / 2
        width: 20 * button.theme.s; height: width
        name: button.icon
        ink: button.hot ? (button.theme.contrast ? "#000000" : "white") : button.theme.textColor
    }
    Text {
        visible: button.caption.length > 0
        anchors.top: glyph.bottom; anchors.topMargin: 3 * button.theme.s
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width - 4; horizontalAlignment: Text.AlignHCenter; elide: Text.ElideRight
        text: button.caption
        color: glyph.ink; font.pixelSize: 10 * button.theme.s; font.bold: true
    }
    // Tooltip on the left.
    Rectangle {
        visible: area.containsMouse && !button.theme.menuOpen && button.tip.length > 0
        anchors.right: parent.left; anchors.rightMargin: 10 * button.theme.s
        anchors.verticalCenter: parent.verticalCenter
        width: tipText.implicitWidth + 20 * button.theme.s; height: tipText.implicitHeight + 10 * button.theme.s
        radius: height / 2
        color: button.theme.contrast ? "#000000" : "#e6202625"
        border.color: button.theme.contrast ? "#ffffff" : "transparent"
        Text { id: tipText; anchors.centerIn: parent; text: button.tip; color: "white"; font.pixelSize: 12 * button.theme.s }
    }
    MouseArea {
        id: area
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: button.activated()
    }
}
