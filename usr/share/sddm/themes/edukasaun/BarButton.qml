// Round button of the login screen's bottom bar: an icon and an optional label.
import QtQuick 2.15

Rectangle {
    id: button
    property var theme
    property string icon: ""
    property string label: ""
    property string tip: ""
    property bool active: false
    property bool danger: false
    signal activated()

    width: label.length > 0 ? caption.implicitWidth + 44 * theme.s : 36 * theme.s
    height: 36 * theme.s
    radius: height / 2
    color: area.containsMouse ? (danger ? "#e5484d" : theme.accent) : (active ? theme.hoverColor : "transparent")
    border.color: active ? theme.accent : "transparent"; border.width: active ? 1 : 0
    Accessible.role: Accessible.Button
    Accessible.name: tip.length > 0 ? tip : label
    Accessible.onPressAction: button.activated()

    Icon {
        id: glyph
        anchors.verticalCenter: parent.verticalCenter
        x: button.label.length > 0 ? 12 * button.theme.s : (parent.width - width) / 2
        width: 18 * button.theme.s; height: width
        name: button.icon
        ink: area.containsMouse ? (button.theme.contrast && !button.danger ? "#000000" : "white") : button.theme.textColor
    }
    Text {
        id: caption
        visible: button.label.length > 0
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: glyph.right; anchors.leftMargin: 7 * button.theme.s
        text: button.label
        color: glyph.ink; font.pixelSize: 13 * button.theme.s; font.bold: true
    }
    // Tooltip above the button.
    Rectangle {
        visible: area.containsMouse && !button.theme.menuOpen && button.tip.length > 0 && button.tip !== button.label
        anchors.bottom: parent.top; anchors.bottomMargin: 8 * button.theme.s
        anchors.horizontalCenter: parent.horizontalCenter
        width: tipText.implicitWidth + 20 * button.theme.s; height: tipText.implicitHeight + 10 * button.theme.s
        radius: height / 2
        color: button.theme.contrast ? "#000000" : "#e6202322"
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
