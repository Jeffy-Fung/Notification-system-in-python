# Notification-system-in-python

<img width="840" height="634" alt="image" src="https://github.com/user-attachments/assets/04582e55-13e9-4155-8cde-5c91cd665547" />

<img width="405" height="580" alt="image" src="https://github.com/user-attachments/assets/e3c4b7de-ac86-4df1-a07c-e4b02ed1afc7" />

## Expected use case

- Simple create notifications by defining:
    - What channels being sent?
    - What is the payload for each channels?
    - Create message template, if channels rely on a template
- Simple create new channels by defining:
    - How does the message being sent? Including inputting the arguments into the message template, if any
    - How to log data?
- Easily add channels to a specific business notification by:
    - Adding the target channel into the `channels` attribute inside the concrete notifications
- Extend notification feature, say user opt-out feature, by extending the abstract notification class


