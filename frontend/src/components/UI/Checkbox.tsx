import { type InputHTMLAttributes, forwardRef } from 'react'

interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label: string
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, className = '', ...props }, ref) => {
    return (
      <label className="flex items-center gap-2 cursor-pointer group">
        <input
          ref={ref}
          type="checkbox"
          className={`
            w-4 h-4 rounded border-gray-300
            text-blue-600 focus:ring-2 focus:ring-blue-500
            cursor-pointer transition-all
            ${className}
          `}
          {...props}
        />
        <span className="text-sm text-gray-700 group-hover:text-gray-900 select-none">
          {label}
        </span>
      </label>
    )
  }
)

Checkbox.displayName = 'Checkbox'
