package main

import (
	"context"
	"errors"
	"net/http"

	"github.com/gin-gonic/gin"
	oryClient "github.com/ory/client-go"
)

// avoid linter removing imports
var _ = oryClient.ContextOAuth2
var _ = context.Background
var _ = errors.New
var _ = gin.Default
var _ = http.DefaultClient

type kratosMiddleware struct {
	client *oryClient.APIClient
}

func NewMiddleware() *kratosMiddleware {
	config := oryClient.NewConfiguration()
	config.Servers = []oryClient.ServerConfiguration{
		{
			URL: "http://127.0.0.1:4434", // kratos admin
		},
	}
	client := oryClient.NewAPIClient(config)
	return &kratosMiddleware{client: client}
}

func (k *kratosMiddleware) Session() gin.HandlerFunc {
	return func(c *gin.Context) {
		session, err := k.validateSession(c.Request)

		if err != nil {
			c.Redirect(http.StatusMovedPermanently, "http://127.0.0.1:4455/login")
			return
		}

		if !*session.Active {
			c.Redirect(http.StatusMovedPermanently, "http://127.0.0.1:4455/login")
			return
		}
		c.Next()
	}
}

func (k *kratosMiddleware) validateSession(r *http.Request) (*oryClient.Session, error) {
	cookie, err := r.Cookie("ory_kratos_session")
	if err != nil {
		return nil, err
	}
	if cookie == nil {
		return nil, errors.New("no cookie")
	}
	resp, _, err := k.client.FrontendApi.ToSession(context.Background()).Cookie(cookie.String()).Execute()
	if err != nil {
		return nil, err
	}
	return resp, nil
}

func main() {
	r := gin.Default()
	mw := NewMiddleware()
	r.Use(mw.Session())
	r.GET("/", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"message": "pong",
		})
	})
	r.Run(":8080")
}
