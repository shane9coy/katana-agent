> ## Documentation Index
> Fetch the complete documentation index at: https://docs.x.com/llms.txt
> Use this file to discover all available pages before exploring further.

# DM
# Direst Message
# Create DM conversation
# Send DM


> Initiates a new direct message conversation with specified participants.

# Create converstaion:

curl --request POST \
  --url https://api.x.com/2/dm_conversations \
  --header 'Authorization: Bearer <token>' \ 
  --header 'Content-Type: application/json' \
  --data '
{
  "conversation_type": "Group",
  "message": {
    "text": "<string>",
    "attachments": [
      {
        "media_id": "1146654567674912769"
      }
    ]
  },
  "participant_ids": [
    "2244994945"
  ]
}
'

 
## OpenAPI Reference

````yaml post /2/dm_conversations
openapi: 3.0.0
info:
  description: X API v2 available endpoints
  version: '2.158'
  title: X API v2
  termsOfService: https://developer.x.com/en/developer-terms/agreement-and-policy.html
  contact:
    name: X Developers
    url: https://developer.x.com/
  license:
    name: X Developer Agreement and Policy
    url: https://developer.x.com/en/developer-terms/agreement-and-policy.html
servers:
  - description: X API
    url: https://api.x.com
security: []
tags:
  - name: Account Activity
    description: Endpoints relating to retrieving, managing AAA subscriptions
    externalDocs:
      description: Find out more
      url: >-
        https://docs.x.com/x-api/enterprise-gnip-2.0/fundamentals/account-activity
  - name: Bookmarks
    description: Endpoints related to retrieving, managing bookmarks of a user
    externalDocs:
      description: Find out more
      url: https://developer.twitter.com/en/docs/twitter-api/bookmarks
  - name: Compliance
    description: Endpoints related to keeping X data in your systems compliant
    externalDocs:
      description: Find out more
      url: >-
        https://developer.twitter.com/en/docs/twitter-api/compliance/batch-tweet/introduction
  - name: Connections
    description: Endpoints related to streaming connections
    externalDocs:
      description: Find out more
      url: https://developer.x.com/en/docs/x-api/connections
  - name: Direct Messages
    description: Endpoints related to retrieving, managing Direct Messages
    externalDocs:
      description: Find out more
      url: https://developer.twitter.com/en/docs/twitter-api/direct-messages
  - name: General
    description: Miscellaneous endpoints for general API functionality
    externalDocs:
      description: Find out more
      url: https://developer.twitter.com/en/docs/twitter-api
  - name: Lists
    description: Endpoints related to retrieving, managing Lists
    externalDocs:
      description: Find out more
      url: https://developer.twitter.com/en/docs/twitter-api/lists
  - name: Marketplace
    description: Endpoints related to marketplace handles
    externalDocs:
      description: Handle marketplace availability
      url: https://docs.x.com/x-api/marketplace/handles/availability
  - name: Media
    description: Endpoints related to Media
    externalDocs:
      description: Find out more
      url: https://developer.x.com
  - name: MediaUpload
    description: Endpoints related to uploading Media
    externalDocs:
      description: Find out more
      url: https://developer.x.com
  - name: News
    description: Endpoint for retrieving news stories
    externalDocs:
      description: Find out more
      url: https://developer.twitter.com/en/docs/twitter-api/news
  - name: Spaces
    description: Endpoints related to retrieving, managing Spaces
    externalDocs:
      description: Find out more
      url: https://developer.twitter.com/en/docs/twitter-api/spaces
  - name: Stream
    description: Endpoints related to streaming
    externalDocs:
      description: Find out more
      url: https://developer.x.com
  - name: Tweets
    description: Endpoints related to retrieving, searching, and modifying Tweets
    externalDocs:
      description: Find out more
      url: https://developer.twitter.com/en/docs/twitter-api/tweets/lookup
  - name: Users
    description: Endpoints related to retrieving, managing relationships of Users
    externalDocs:
      description: Find out more
      url: https://developer.twitter.com/en/docs/twitter-api/users/lookup
paths:
  /2/dm_conversations:
    post:
      tags:
        - Direct Messages
      summary: Create DM conversation
      description: Initiates a new direct message conversation with specified participants.
      operationId: createDirectMessagesConversation
      parameters: []
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateDmConversationRequest'
      responses:
        '201':
          description: The request has succeeded.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CreateDmEventResponse'
        default:
          description: The request has failed.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
            application/problem+json:
              schema:
                $ref: '#/components/schemas/Problem'
      security:
        - OAuth2UserToken:
            - dm.write
            - tweet.read
            - users.read
        - UserToken: []
components:
  schemas:
    CreateDmConversationRequest:
      type: object
      required:
        - conversation_type
        - participant_ids
        - message
      properties:
        conversation_type:
          type: string
          description: The conversation type that is being created.
          enum:
            - Group
        message:
          $ref: '#/components/schemas/CreateMessageRequest'
        participant_ids:
          $ref: '#/components/schemas/DmParticipants'
      additionalProperties: false
    CreateDmEventResponse:
      type: object
      properties:
        data:
          type: object
          required:
            - dm_conversation_id
            - dm_event_id
          properties:
            dm_conversation_id:
              $ref: '#/components/schemas/DmConversationId'
            dm_event_id:
              $ref: '#/components/schemas/DmEventId'
        errors:
          type: array
          minItems: 1
          items:
            $ref: '#/components/schemas/Problem'
    Error:
      type: object
      required:
        - code
        - message
      properties:
        code:
          type: integer
          format: int32
        message:
          type: string
    Problem:
      type: object
      description: >-
        An HTTP Problem Details object, as defined in IETF RFC 7807
        (https://tools.ietf.org/html/rfc7807).
      required:
        - type
        - title
      properties:
        detail:
          type: string
        status:
          type: integer
        title:
          type: string
        type:
          type: string
      discriminator:
        propertyName: type
        mapping:
          about:blank: '#/components/schemas/GenericProblem'
          https://api.twitter.com/2/problems/client-disconnected: '#/components/schemas/ClientDisconnectedProblem'
          https://api.twitter.com/2/problems/client-forbidden: '#/components/schemas/ClientForbiddenProblem'
          https://api.twitter.com/2/problems/conflict: '#/components/schemas/ConflictProblem'
          https://api.twitter.com/2/problems/disallowed-resource: '#/components/schemas/DisallowedResourceProblem'
          https://api.twitter.com/2/problems/duplicate-rules: '#/components/schemas/DuplicateRuleProblem'
          https://api.twitter.com/2/problems/invalid-request: '#/components/schemas/InvalidRequestProblem'
          https://api.twitter.com/2/problems/invalid-rules: '#/components/schemas/InvalidRuleProblem'
          https://api.twitter.com/2/problems/noncompliant-rules: '#/components/schemas/NonCompliantRulesProblem'
          https://api.twitter.com/2/problems/not-authorized-for-field: '#/components/schemas/FieldUnauthorizedProblem'
          https://api.twitter.com/2/problems/not-authorized-for-resource: '#/components/schemas/ResourceUnauthorizedProblem'
          https://api.twitter.com/2/problems/operational-disconnect: '#/components/schemas/OperationalDisconnectProblem'
          https://api.twitter.com/2/problems/resource-not-found: '#/components/schemas/ResourceNotFoundProblem'
          https://api.twitter.com/2/problems/resource-unavailable: '#/components/schemas/ResourceUnavailableProblem'
          https://api.twitter.com/2/problems/rule-cap: '#/components/schemas/RulesCapProblem'
          https://api.twitter.com/2/problems/streaming-connection: '#/components/schemas/ConnectionExceptionProblem'
          https://api.twitter.com/2/problems/unsupported-authentication: '#/components/schemas/UnsupportedAuthenticationProblem'
          https://api.twitter.com/2/problems/usage-capped: '#/components/schemas/UsageCapExceededProblem'
    CreateMessageRequest:
      anyOf:
        - $ref: '#/components/schemas/CreateTextMessageRequest'
        - $ref: '#/components/schemas/CreateAttachmentsMessageRequest'
    DmParticipants:
      type: array
      description: Participants for the DM Conversation.
      minItems: 2
      maxItems: 49
      items:
        $ref: '#/components/schemas/UserId'
    DmConversationId:
      type: string
      description: >-
        Unique identifier of a DM conversation. This can either be a numeric
        string, or a pair of numeric strings separated by a '-' character in the
        case of one-on-one DM Conversations.
      pattern: ^([0-9]{1,19}-[0-9]{1,19}|[0-9]{15,19})$
      example: 123123123-456456456
    DmEventId:
      type: string
      description: Unique identifier of a DM Event.
      pattern: ^[0-9]{1,19}$
      example: '1146654567674912769'
    CreateTextMessageRequest:
      type: object
      required:
        - text
      properties:
        attachments:
          $ref: '#/components/schemas/DmAttachments'
        text:
          type: string
          description: Text of the message.
          minLength: 1
    CreateAttachmentsMessageRequest:
      type: object
      required:
        - attachments
      properties:
        attachments:
          $ref: '#/components/schemas/DmAttachments'
        text:
          type: string
          description: Text of the message.
          minLength: 1
    UserId:
      type: string
      description: >-
        Unique identifier of this User. This is returned as a string in order to
        avoid complications with languages and tools that cannot handle large
        integers.
      pattern: ^[0-9]{1,19}$
      example: '2244994945'
    DmAttachments:
      type: array
      description: Attachments to a DM Event.
      items:
        $ref: '#/components/schemas/DmMediaAttachment'
    DmMediaAttachment:
      type: object
      required:
        - media_id
      properties:
        media_id:
          $ref: '#/components/schemas/MediaId'
    MediaId:
      type: string
      description: The unique identifier of this Media.
      pattern: ^[0-9]{1,19}$
      example: '1146654567674912769'
  securitySchemes:
    OAuth2UserToken:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://api.x.com/2/oauth2/authorize
          tokenUrl: https://api.x.com/2/oauth2/token
          scopes:
            block.read: View accounts you have blocked.
            bookmark.read: Read your bookmarked Posts.
            bookmark.write: Create and delete your bookmarks.
            dm.read: Read all your Direct Messages.
            dm.write: Send and manage your Direct Messages.
            follows.read: View accounts you follow and accounts following you.
            follows.write: Follow and unfollow accounts on your behalf.
            like.read: View Posts you have liked and likes you can see.
            like.write: Like and unlike Posts on your behalf.
            list.read: >-
              View Lists, members, and followers of Lists you created or are a
              member of, including private Lists.
            list.write: Create and manage Lists on your behalf.
            media.write: Upload media, such as photos and videos, on your behalf.
            mute.read: View accounts you have muted.
            mute.write: Mute and unmute accounts on your behalf.
            offline.access: Request a refresh token for the app.
            space.read: View all Spaces you have access to.
            timeline.read: >-
              View all Custom Timelines you can see, including public Custom
              Timelines from other developers.
            tweet.moderate.write: Hide and unhide replies to your Posts.
            tweet.read: >-
              View all Posts you can see, including those from protected
              accounts.
            tweet.write: Post and repost on your behalf.
            users.read: View any account you can see, including protected accounts.
    UserToken:
      type: http
      scheme: OAuth

````
