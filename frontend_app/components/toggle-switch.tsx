"use client"

import * as React from "react"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"

interface ToggleSwitchProps {
  label?: string
  defaultChecked?: boolean
  onToggle?: (checked: boolean) => void
  disabled?: boolean
  className?: string
}

export function ToggleSwitch({
  label,
  defaultChecked = false,
  onToggle,
  disabled = false,
  className = "",
}: ToggleSwitchProps) {
  const [checked, setChecked] = React.useState(defaultChecked)

  const handleCheckedChange = (checked: boolean) => {
    setChecked(checked)
    if (onToggle) {
      onToggle(checked)
    }
  }

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <Switch id="toggle-switch" checked={checked} onCheckedChange={handleCheckedChange} disabled={disabled} />
      {label && <Label htmlFor="toggle-switch">{label}</Label>}
    </div>
  )
}
