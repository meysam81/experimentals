package main

import (
	"net/http"
	"os"

	"github.com/labstack/echo/v4"
)

func getEnv(key, fallback string) string {
	value, exists := os.LookupEnv(key)
	if !exists {
		value = fallback
	}
	return value
}

func targets() []map[string]interface{} {
	// 	[
	//   {
	//     "targets": [ "<host>", ... ],
	//     "labels": {
	//       "<labelname>": "<labelvalue>", ...
	//     }
	//   },
	//   ...
	// ]
	return []map[string]interface{}{
		{
			"targets": []string{"localhost:9090"},
			"labels": map[string]string{
				"job": "prometheus",
			},
		},
	}

}

func main() {
	port := getEnv("PORT", "1323")

	e := echo.New()
	// set log level to debug
	e.Logger.SetLevel(1)
	e.GET("/", func(c echo.Context) error {
		return c.JSON(http.StatusOK, targets())
	})
	e.Logger.Fatal(e.Start(":" + port))
}
