export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection and try again.',
  UNAUTHORIZED: 'Invalid credentials. Please check your email and password.',
  FORBIDDEN: 'You do not have permission to perform this action.',
  NOT_FOUND: 'The requested resource was not found.',
  SERVER_ERROR: 'Server error. Please try again later.',
  UNKNOWN_ERROR: 'An unexpected error occurred. Please try again.',
} as const;

export interface ApiError {
  message?: string;
  response?: {
    status?: number;
    data?: {
      message?: string;
      detail?: string;
    };
  };
}

export const handleApiError = (error: ApiError): string => {
  // Network errors
  if (!error.response && error.message === 'Network Error') {
    return ERROR_MESSAGES.NETWORK_ERROR;
  }

  // HTTP status errors
  const status = error.response?.status;
  if (status === 401) {
    return ERROR_MESSAGES.UNAUTHORIZED;
  }
  if (status === 403) {
    return ERROR_MESSAGES.FORBIDDEN;
  }
  if (status === 404) {
    return ERROR_MESSAGES.NOT_FOUND;
  }
  if (status && status >= 500) {
    return ERROR_MESSAGES.SERVER_ERROR;
  }

  // API error messages
  const apiMessage = error.response?.data?.detail || error.response?.data?.message || error.message;
  if (apiMessage) {
    return apiMessage;
  }

  return ERROR_MESSAGES.UNKNOWN_ERROR;
};