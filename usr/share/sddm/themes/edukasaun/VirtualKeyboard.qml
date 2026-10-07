// On-screen keyboard (Qt Virtual Keyboard). Loaded only when the
// qml-module-qtquick-virtualkeyboard (Qt 5) or qml6-module-qtquick-virtualkeyboard
// (Qt 6) package is installed; otherwise Main.qml hides the option.
import QtQuick 2.15
import QtQuick.VirtualKeyboard 2.1

InputPanel {
    id: panel
    active: true
}
