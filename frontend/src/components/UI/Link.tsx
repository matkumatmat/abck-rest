import { Link as RouterLink, type LinkProps as RouterLinkProps } from '@tanstack/react-router'
import { type ReactNode } from 'react'

interface LinkProps extends Omit<RouterLinkProps, 'children'> {
  children: ReactNode
  variant?: 'default' | 'primary' | 'subtle'
}

export function Link({ children, variant = 'default', className = '', ...props }: LinkProps) {
  const variantStyles = {
    default: 'text-blue-600 hover:text-blue-800 hover:underline',
    primary: 'text-gray-900 font-semibold hover:text-gray-700',
    subtle: 'text-gray-600 hover:text-gray-900 hover:underline',
  }

  return (
    <RouterLink
      className={`transition-colors duration-200 ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </RouterLink>
  )
}
